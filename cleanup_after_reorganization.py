"""
Cleanup Script After Reorganization
This script:
1. Fixes up redirectors (updates references)
2. Removes empty folders
3. Verifies the reorganization

Run this AFTER you've completed the reorganization with dry_run=False
"""

import unreal

class ContentCleanup:
    def __init__(self):
        self.editor_asset_lib = unreal.EditorAssetLibrary()
        self.asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    
    def fix_redirectors_in_folder(self, folder_path):
        """Fix up redirectors in a specific folder"""
        print(f"\nFixing redirectors in: {folder_path}")
        
        if not self.editor_asset_lib.does_directory_exist(folder_path):
            print(f"  Folder doesn't exist: {folder_path}")
            return 0
        
        # Get all assets in folder
        assets = self.asset_registry.get_assets_by_path(folder_path, recursive=True)
        
        redirectors = []
        for asset in assets:
            asset_class = str(asset.asset_class_path.asset_name)
            if 'Redirector' in asset_class or 'ObjectRedirector' in asset_class:
                redirectors.append(str(asset.package_name))
        
        if redirectors:
            print(f"  Found {len(redirectors)} redirectors to fix")
            # Fix redirectors
            fixed = self.editor_asset_lib.consolidate_assets(
                asset_to_consolidate_to=redirectors[0],
                assets_to_consolidate=redirectors
            ) if len(redirectors) > 0 else True
            
            # Delete redirectors after fixing
            for redirector_path in redirectors:
                try:
                    self.editor_asset_lib.delete_asset(redirector_path)
                    print(f"    ✓ Deleted redirector: {redirector_path}")
                except:
                    pass
            
            return len(redirectors)
        else:
            print(f"  No redirectors found")
            return 0
    
    def fix_all_redirectors(self):
        """Fix redirectors in all relevant folders"""
        print("\n" + "="*60)
        print("STEP 1: FIXING REDIRECTORS")
        print("="*60)
        
        folders_to_check = [
            "/Game/DBV",
            "/Game/Courses",
            "/Game/TopDown",
            "/Game/Input",
            "/Game/External/DBV",
            "/Game/Levels/Maps",
            "/Game/Core/Blueprints/Player",
            "/Game/Core/Blueprints/Gameplay",
            "/Game/UI/VirtualJoystick"
        ]
        
        total_fixed = 0
        for folder in folders_to_check:
            fixed = self.fix_redirectors_in_folder(folder)
            total_fixed += fixed
        
        print(f"\nTotal redirectors fixed: {total_fixed}")
        return total_fixed
    
    def check_folder_empty(self, folder_path):
        """Check if a folder is empty (no assets)"""
        if not self.editor_asset_lib.does_directory_exist(folder_path):
            return None  # Doesn't exist
        
        assets = self.asset_registry.get_assets_by_path(folder_path, recursive=True)
        return len(list(assets)) == 0
    
    def delete_empty_folder(self, folder_path):
        """Delete an empty folder"""
        try:
            # Unreal doesn't have a direct "delete directory" in EditorAssetLibrary
            # We need to use the AssetTools
            print(f"  Manual cleanup needed: {folder_path}")
            print(f"    → Right-click in Content Browser → Delete")
            return False
        except Exception as e:
            print(f"  Error: {e}")
            return False
    
    def find_empty_folders(self):
        """Find and report empty folders"""
        print("\n" + "="*60)
        print("STEP 2: FINDING EMPTY FOLDERS")
        print("="*60)
        
        folders_to_check = [
            "/Game/DBV",
            "/Game/Courses", 
            "/Game/TopDown",
            "/Game/Input"
        ]
        
        empty_folders = []
        
        for folder in folders_to_check:
            is_empty = self.check_folder_empty(folder)
            
            if is_empty is None:
                print(f"✓ Already deleted: {folder}")
            elif is_empty:
                print(f"⚠️  Empty folder found: {folder}")
                empty_folders.append(folder)
            else:
                # Count remaining assets
                assets = self.asset_registry.get_assets_by_path(folder, recursive=True)
                asset_count = len(list(assets))
                print(f"⚠️  Folder still has {asset_count} assets: {folder}")
                
                # List what's still there
                if asset_count > 0 and asset_count <= 10:
                    print(f"    Remaining assets:")
                    for asset in list(assets)[:10]:
                        print(f"      - {asset.asset_name} ({asset.asset_class_path.asset_name})")
        
        return empty_folders
    
    def manual_cleanup_instructions(self, empty_folders):
        """Provide manual cleanup instructions"""
        print("\n" + "="*60)
        print("STEP 3: MANUAL CLEANUP INSTRUCTIONS")
        print("="*60)
        
        if not empty_folders:
            print("\n✅ No empty folders found! Cleanup complete.")
            return
        
        print("\nTo delete empty folders manually:")
        print("-" * 60)
        print("1. Open Content Browser in Unreal Editor")
        print("2. Navigate to each folder below:")
        print()
        
        for folder in empty_folders:
            folder_name = folder.replace("/Game/", "")
            print(f"   • {folder_name}")
        
        print("\n3. Right-click on each folder")
        print("4. Select 'Delete'")
        print("5. Confirm deletion")
        print()
        print("OR you can delete them all at once:")
        print("  - Select all empty folders (Ctrl+Click)")
        print("  - Right-click → Delete")
        print("  - Confirm")
    
    def verify_reorganization(self):
        """Verify the reorganization was successful"""
        print("\n" + "="*60)
        print("STEP 4: VERIFICATION")
        print("="*60)
        
        checks = {
            "External/DBV exists": self.editor_asset_lib.does_directory_exist("/Game/External/DBV"),
            "Levels/Maps exists": self.editor_asset_lib.does_directory_exist("/Game/Levels/Maps"),
            "Core/Blueprints/Player exists": self.editor_asset_lib.does_directory_exist("/Game/Core/Blueprints/Player"),
            "Core/Blueprints/Gameplay exists": self.editor_asset_lib.does_directory_exist("/Game/Core/Blueprints/Gameplay"),
            "UI/VirtualJoystick exists": self.editor_asset_lib.does_directory_exist("/Game/UI/VirtualJoystick"),
        }
        
        # Count assets in new locations
        asset_counts = {}
        for folder_name, folder_path in [
            ("External/DBV", "/Game/External/DBV"),
            ("Levels/Maps", "/Game/Levels/Maps"),
            ("Core/Blueprints/Player", "/Game/Core/Blueprints/Player"),
            ("Core/Blueprints/Gameplay", "/Game/Core/Blueprints/Gameplay"),
            ("UI/VirtualJoystick", "/Game/UI/VirtualJoystick")
        ]:
            if self.editor_asset_lib.does_directory_exist(folder_path):
                assets = self.asset_registry.get_assets_by_path(folder_path, recursive=True)
                asset_counts[folder_name] = len(list(assets))
            else:
                asset_counts[folder_name] = 0
        
        print("\nFolder Existence Check:")
        for check, result in checks.items():
            status = "✓" if result else "✗"
            print(f"  {status} {check}")
        
        print("\nAsset Counts in New Locations:")
        for folder, count in asset_counts.items():
            print(f"  {folder}: {count} assets")
        
        print("\nExpected Results:")
        print("  - External/DBV: ~203 assets")
        print("  - Levels/Maps: ~2+ maps")
        print("  - Core/Blueprints/*: ~10+ blueprints")
        print("  - UI/VirtualJoystick: ~3+ assets")
        
        # Check if everything looks good
        all_good = all(checks.values()) and asset_counts["External/DBV"] > 100
        
        if all_good:
            print("\n✅ Reorganization verified successfully!")
        else:
            print("\n⚠️  Some issues detected - review counts above")
    
    def execute_cleanup(self):
        """Execute the full cleanup process"""
        print("\n" + "#"*60)
        print("#  CONTENT CLEANUP AFTER REORGANIZATION")
        print("#"*60)
        
        # Step 1: Fix redirectors
        self.fix_all_redirectors()
        
        # Step 2: Find empty folders
        empty_folders = self.find_empty_folders()
        
        # Step 3: Provide manual cleanup instructions
        self.manual_cleanup_instructions(empty_folders)
        
        # Step 4: Verify reorganization
        self.verify_reorganization()
        
        # Final instructions
        print("\n" + "="*60)
        print("FINAL STEPS")
        print("="*60)
        print("1. Delete empty folders manually (see instructions above)")
        print("2. In Content Browser: Right-click Content → Fix Up Redirectors in Folder")
        print("3. File → Save All (Ctrl+Shift+S)")
        print("4. Test your game (Play In Editor)")
        print("5. Commit changes to source control")
        print("\n✅ Cleanup script complete!")

# Execute
if __name__ == "__main__":
    cleanup = ContentCleanup()
    cleanup.execute_cleanup()
