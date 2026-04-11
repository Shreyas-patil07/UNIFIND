#!/usr/bin/env python3
"""Quick test to verify needs module imports correctly."""

import sys
sys.path.insert(0, 'backend')

try:
    from routes import needs
    print("✅ needs module imported successfully")
    print(f"✅ Router object exists: {hasattr(needs, 'router')}")
    
    if hasattr(needs, 'router'):
        routes = needs.router.routes
        print(f"✅ Number of routes: {len(routes)}")
        print("\nRegistered endpoints:")
        for route in routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"  {list(route.methods)[0]:6s} {route.path}")
    
    print("\n✅ All checks passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
