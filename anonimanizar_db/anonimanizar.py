import os, sys, re, json, subprocess
import pandas as pd
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.dialects.postgresql import UUID
from faker import Faker
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

class AgnosticAnonymizer:
    def __init__(self, config_path='config.json'):
        self.config = self._load_config(config_path)
        self.source_uri = os.getenv('DB_SOURCE_URL')
        self.target_uri = os.getenv('DB_TARGET_URL')
        self.fake = Faker(os.getenv('FAKER_LOCALE', 'es_AR'))

        if not self.source_uri or not self.target_uri:
            print("Error: URIs no definidas en el .env")
            sys.exit(1)

        self.src_engine = create_engine(self.source_uri)
        self.tgt_engine = None 

    def _load_config(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def prepare_environment(self):
        """Crea la base de datos y clona el esquema."""
        t = urlparse(self.target_uri)
        s = urlparse(self.source_uri)
        target_db = t.path.lstrip('/')
        target_db_quoted = f'"{target_db}"'

        admin_uri = f"{t.scheme}://{t.username}:{t.password}@{t.hostname}:{t.port}/postgres"
        admin_engine = create_engine(admin_uri, isolation_level="AUTOCOMMIT")
        with admin_engine.connect() as conn:
            conn.execute(text(f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{target_db}' AND pid <> pg_backend_pid()"))
            conn.execute(text(f"DROP DATABASE IF EXISTS {target_db_quoted}"))
            conn.execute(text(f"CREATE DATABASE {target_db_quoted}"))
        admin_engine.dispose()

        # 2. Clonar Esquema
        print("[*] Clonando esquema vía pg_dump...")
        dump_cmd = (
            f"PGPASSWORD='{s.password}' pg_dump -s -h {s.hostname} -p {s.port} -U {s.username} {s.path.lstrip('/')} | "
            f"PGPASSWORD='{t.password}' psql -h {t.hostname} -p {t.port} -U {t.username} -d {target_db_quoted}"
        )
        subprocess.run(dump_cmd, shell=True, check=True, capture_output=True)
        self.tgt_engine = create_engine(self.target_uri)

    def _get_faker_value(self, method_str):
        try:
            if '(' in method_str:
                match = re.match(r"(\w+)\(['\"](.+)['\"]", method_str)
                if match:
                    func_name, arg = match.groups()
                    return getattr(self.fake, func_name)(arg)
            func = self.fake
            for part in method_str.split('.'):
                func = getattr(func, part)
            return func()
        except: return None

    def _get_excluded_ids(self, query):
        if not query: return set()
        try:
            with self.src_engine.connect() as conn:
                res = conn.execute(text(query))
                return {row[0] for row in res}
        except: return set()

    def run(self):
        self.prepare_environment()
        inspector = inspect(self.src_engine)
        all_tables = inspector.get_table_names(schema='public')
        config_tables = self.config.get('tables', {})

        # Usamos UNA SOLA CONEXIÓN para todo el proceso de carga
        # Esto permite mantener el 'session_replication_role' activo
        with self.tgt_engine.connect() as tgt_conn:
            print("[*] Desactivando temporalmente restricciones de integridad...")
            tgt_conn.execute(text("SET session_replication_role = 'replica';"))
            
            tables_list = ", ".join([f"public.\"{t}\"" for t in all_tables])
            tgt_conn.execute(text(f"TRUNCATE TABLE {tables_list} RESTART IDENTITY CASCADE;"))
            tgt_conn.commit()

            print(f"\n--- Iniciando Transferencia ({len(all_tables)} tablas) ---")
            for table_name in all_tables:
                full_name = f"public.{table_name}"
                print(f">> {full_name}", end="\r")

                try:
                    # Detectar UUIDs
                    columns_info = inspector.get_columns(table_name, schema='public')
                    dtype_map = {col['name']: UUID(as_uuid=True) for col in columns_info if 'UUID' in str(col['type']).upper()}

                    # Leer y procesar
                    for df in pd.read_sql(f'SELECT * FROM {full_name}', self.src_engine, chunksize=5000):
                        if full_name in config_tables:
                            settings = config_tables[full_name]
                            excluded_ids = self._get_excluded_ids(settings.get('filter_query'))
                            id_col = settings.get('filter_column', 'id')
                            
                            for col, method in settings.get('anonymize', {}).items():
                                if col in df.columns:
                                    mask = ~df[id_col].isin(excluded_ids) if (excluded_ids and id_col in df.columns) else pd.Series([True]*len(df))
                                    df.loc[mask, col] = [self._get_faker_value(method) for _ in range(mask.sum())]

                        # Serializar JSONB
                        for col in df.columns:
                            if df[col].dtype == 'object':
                                sample = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
                                if isinstance(sample, (dict, list)):
                                    df[col] = df[col].apply(lambda x: json.dumps(x) if x is not None else None)

                        # Insertar
                        df.to_sql(table_name, tgt_conn, schema='public', if_exists='append', index=False, dtype=dtype_map, method='multi', chunksize=1000)
                    
                    print(f">> {full_name} [OK]                    ")

                except Exception as e:
                    print(f"\n>> {full_name} [ERROR]: {e}")

            print("[*] Reactivando restricciones de integridad...")
            tgt_conn.execute(text("SET session_replication_role = 'origin';"))
            tgt_conn.commit()

if __name__ == "__main__":
    AgnosticAnonymizer().run()
    print("\n[FIN] Proceso completado exitosamente.")