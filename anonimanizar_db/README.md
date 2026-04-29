# Anonimizador de Base de Datos

Script Python que copia una base de datos PostgreSQL de origen a una de destino, aplicando datos falsos a los campos sensibles configurados. El esquema se clona exactamente (índices, constraints, FK), y solo los datos son modificados.


## Instalación de dependencias

```bash
pip install sqlalchemy psycopg2-binary pandas faker python-dotenv
```
---

## Configuración del `.env`

Copiar `.env.template` a `.env` y completar los valores:


```env
DB_SOURCE_URL=postgresql://usuario:password@host:5432/db_produccion

DB_TARGET_URL=postgresql://usuario:password@host:5432/db_anonimizada

FAKER_LOCALE=es_AR
```

 `DB_SOURCE_URL`  URI de la base de datos **origen** (producción o dump restaurado) 
 `DB_TARGET_URL`  URI de la base de datos **destino** — se recrea en cada ejecución 
 `FAKER_LOCALE`  Locale de Faker para datos realistas. Ej: es_AR 


---

## Configuración del `config.json`

Define qué tablas y columnas se anonimizan. Las tablas no listadas se copian tal cual.

### Estructura general

```json
{
  "tables": {
    "public.nombre_tabla": {
      "anonymize": {
        "columna": "metodo_faker"
      },
      "filter_query": "SELECT id FROM public.otra_tabla WHERE condicion",
      "filter_column": "id"
    }
  }
}
```


| Clave | Requerida | Descripción |
| `anonymize` | Sí | Mapa de `columna → método Faker` a aplicar |
| `filter_query` | No | SQL que devuelve IDs a **excluir** de la anonimización |
| `filter_column` | No | Columna de la tabla que se compara con los IDs del `filter_query` (default: `id`) |

### Métodos Faker disponibles

Cualquier método de la librería [Faker](https://faker.readthedocs.io/en/master/) puede usarse. Ejemplos comunes:

 Método en config | Dato generado |
 `first_name` | Nombre de pila |
 `last_name` | Apellido |
 `email` | Email aleatorio |
 `unique.email` | Email único (no repite valores) |
 `phone_number` | Número de teléfono |
 `street_name` | Nombre de calle |
 `company` | Nombre de empresa |
 `city` | Ciudad |
 `password` | Hash de contraseña |
 `numerify('########')` | Número con la cantidad de dígitos indicada por `#` |

#### Uso de `numerify`
Para generar números de longitud fija (DNI, CUIT, etc.) usar la sintaxis con paréntesis:

```json
"dni": "numerify('########')",
"cuit": "numerify('###########')"
```
Cada `#` es reemplazado por un dígito aleatorio del 0 al 9.


```bash
python anonimanizar.py
```

