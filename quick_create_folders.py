"""
Quick Folder Structure Creator for Unreal Engine
Run this in Unreal's Python Console to create the folder structure instantly.

Usage:
1. Copy this entire file
2. Open Unreal Editor
3. Window → Developer Tools → Python Console
4. Paste and press Enter
"""

import unreal

def create_folder_structure():
    """Create the complete folder structure for the project"""
    
    editor_asset_lib = unreal.EditorAssetLibrary()
    
    # Define all folders to create
    folders = [
        # Core folders
        '/Game/Core',
        '/Game/Core/Blueprints',
        '/Game/Core/Blueprints/Player',
        '/Game/Core/Blueprints/Gameplay',
        '/Game/Core/Blueprints/Environment',
        '/Game/Core/Materials',
        '/Game/Core/Textures',
        
        # UI folders
        '/Game/UI',
        '/Game/UI/VirtualJoystick',
        '/Game/UI/Widgets',
        '/Game/UI/HUD',
        
        # Level folders
        '/Game/Levels',
        '/Game/Levels/Maps',
        '/Game/Levels/Sublevels',
        
        # External assets folders
        '/Game/External',
        '/Game/External/DBV',
    ]
    
    print("\n" + "="*60)
    print("Creating Folder Structure")
    print("="*60 + "\n")
    
    created = []
    existing = []
    failed = []
    
    for folder in folders:
        if editor_asset_lib.does_directory_exist(folder):
            existing.append(folder)
            print(f"✓ Already exists: {folder}")
        else:
            success = editor_asset_lib.make_directory(folder)
            if success:
                created.append(folder)
                print(f"✓ Created: {folder}")
            else:
                failed.append(folder)
                print(f"✗ Failed: {folder}")
    
    # Summary
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    print(f"Created: {len(created)} folders")
    print(f"Already existed: {len(existing)} folders")
    print(f"Failed: {len(failed)} folders")
    
    if failed:
        print("\n⚠️  Some folders failed to create:")
        for folder in failed:
            print(f"  - {folder}")
    else:
        print("\n✅ All folders created successfully!")
    
    print("\n" + "="*60)
    print("Next Steps:")
    print("="*60)
    print("1. Refresh Content Browser (right-click → Refresh)")
    print("2. Start moving assets to appropriate folders")
    print("3. Move DBV folder to External/DBV")
    print("4. Move maps to Levels/Maps")
    print("5. Categorize blueprints into Player/Gameplay/Environment")
    print("\nRefer to REORGANIZATION_GUIDE.md for detailed instructions")
    print("="*60 + "\n")
    
    return {
        'created': created,
        'existing': existing,
        'failed': failed
    }

# Execute
if __name__ == "__main__":
    result = create_folder_structure()
