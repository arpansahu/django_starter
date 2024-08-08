1. Test DB
  Django management command designed to test the basic functionality of the database. It performs a series of CRUD (Create, Read, Update, Delete) operations to ensure the database is working correctly.
```bash
python manage.py test_db
```

2. Test Cache
   Django management command designed to test the basic functionality of the caching system. It performs a set and get operation to ensure the cache is working correctly and validates the expiration of cache entries.
```bash
python manage.py test_cache
```