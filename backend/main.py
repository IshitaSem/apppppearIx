

honest-renewal

production

2

Trial



apppppearIx
Deployments
Variables
Metrics
Settings
Unexposed service
3.11.15python@3.11.15
us-west2
1 Replica




History



















apppppearIx
/
16684467
Removed

Apr 15, 2026, 9:41 PM GMT+5:30
DetailsBuildDeployNetwork Flow
Filter and search logs

    config.load()
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/config.py", line 467, in load
    self.loaded_app = import_from_string(self.app)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/importer.py", line 21, in import_from_string
    module = importlib.import_module(module_str)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mise/installs/python/3.11.15/lib/python3.11/importlib/__init__.py", line 126, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 940, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
  File "/app/main.py", line 30, in <module>
    from outfit import router as outfit_router
  File "/app/outfit.py", line 2, in <module>
    from database import outfits
ImportError: cannot import name 'outfits' from 'database' (/app/database.py)
WARNING:upload:rembg disabled for production/Railway deployment
  File "/app/.venv/lib/python3.11/site-packages/click/core.py", line 824, in invoke
    return callback(*args, **kwargs)
Traceback (most recent call last):
  File "/app/.venv/bin/uvicorn", line 8, in <module>
    sys.exit(main())
             ^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/click/core.py", line 1485, in __call__
    return self.main(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/click/core.py", line 1406, in main
    rv = self.invoke(ctx)
         ^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/click/core.py", line 1269, in invoke
    return ctx.invoke(self.callback, **ctx.params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/main.py", line 416, in main
    run(
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/main.py", line 587, in run
    server.run()
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/server.py", line 61, in run
    return asyncio.run(self.serve(sockets=sockets))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mise/installs/python/3.11.15/lib/python3.11/asyncio/runners.py", line 190, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/mise/installs/python/3.11.15/lib/python3.11/asyncio/runners.py", line 118, in run
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mise/installs/python/3.11.15/lib/python3.11/asyncio/base_events.py", line 654, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/server.py", line 68, in serve
    config.load()
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/config.py", line 467, in load
    self.loaded_app = import_from_string(self.app)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/importer.py", line 21, in import_from_string
    module = importlib.import_module(module_str)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mise/installs/python/3.11.15/lib/python3.11/importlib/__init__.py", line 126, in import_module
  File "/app/main.py", line 30, in <module>
    from outfit import router as outfit_router
  File "/app/outfit.py", line 2, in <module>
    from database import outfits
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ImportError: cannot import name 'outfits' from 'database' (/app/database.py)
  File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 940, in exec_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
WARNING:upload:rembg disabled for production/Railway deployment
Traceback (most recent call last):
  File "/app/.venv/bin/uvicorn", line 8, in <module>
    sys.exit(main())
  File "/app/.venv/lib/python3.11/site-packages/click/core.py", line 1485, in __call__
    return self.main(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/click/core.py", line 1406, in main
    rv = self.invoke(ctx)
         ^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/click/core.py", line 1269, in invoke
    return ctx.invoke(self.callback, **ctx.params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    return callback(*args, **kwargs)
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/main.py", line 416, in main
    run(
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/main.py", line 587, in run
    server.run()
    return asyncio.run(self.serve(sockets=sockets))
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mise/installs/python/3.11.15/lib/python3.11/asyncio/runners.py", line 190, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/mise/installs/python/3.11.15/lib/python3.11/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mise/installs/python/3.11.15/lib/python3.11/asyncio/base_events.py", line 654, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/server.py", line 68, in serve
    config.load()
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/config.py", line 467, in load
    self.loaded_app = import_from_string(self.app)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/.venv/lib/python3.11/site-packages/uvicorn/importer.py", line 21, in import_from_string
    module = importlib.import_module(module_str)
  File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 940, in exec_module
  File "/mise/installs/python/3.11.15/lib/python3.11/importlib/__init__.py", line 126, in import_module
  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
    from outfit import router as outfit_router
  File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
  File "/app/outfit.py", line 2, in <module>
    from database import outfits
ImportError: cannot import name 'outfits' from 'database' (/app/database.py)
You reached the end of the range
Apr 15, 2026, 9:42 PM
