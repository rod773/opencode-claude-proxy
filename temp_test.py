import os
os.environ['ANTHROPIC_API_KEY'] = 'test'

try:
    import server.main as sm
    print('Import succeeded')
except Exception as e:
    print('Import failed:', e)
