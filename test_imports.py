
try:
    print("Importing cryptography...")
    import cryptography
    print("cryptography imported successfully")
except ImportError as e:
    print(f"Failed to import cryptography: {e}")

try:
    print("Importing pydantic...")
    import pydantic
    print("pydantic imported successfully")
except ImportError as e:
    print(f"Failed to import pydantic: {e}")

try:
    print("Importing supabase...")
    import supabase
    print("supabase imported successfully")
except ImportError as e:
    print(f"Failed to import supabase: {e}")
