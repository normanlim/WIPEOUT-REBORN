"""
Simplified Unreal Engine Content Reorganization Script
More robust and easier to debug version

Your Project Structure:
- Characters/ (128 assets) - Keep as is
- Courses/ (2 maps) → Move to Levels/Maps/
- Cursor/ (4 assets) - Keep as is  
- DBV/ (203 assets) → Move to External/DBV/
- Input/ (10 assets) → Move appropriate parts to UI/ or Core/
- LevelPrototyping/ (26 assets) - Keep as is
- StarterContent/ (267 assets) - Keep as is (Epic's content)
- TopDown/ (24 assets) → Organize into Core/Blueprints/

Usage: Run in Unreal Python Console
"""

import unreal

class SimpleReorganizer:
    def __init__(self):
        self.asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
        self.editor_asset_lib = unreal.EditorAssetLibrary()
        
    def get_all_assets_in_path(self, path):
        """Get all assets in a specific path"""
        try:
            assets = self.asset_registry.get_assets_by_path(path, recursive=True)
            return list(assets)
        except Exception as e:
            print(f"Error getting assets from {path}: {e}")
            return []
    
    def move_asset(self, source_path, target_path, dry_run=True):
        """Move a single asset"""
        if dry_run:
            print(f"  [DRY RUN] Would move: {source_path} → {target_path}")
            return True
        else:
            try:
                success = self.editor_asset_lib.rename_asset(source_path, target_path)
                if success:
                    print(f"  ✓ Moved: {source_path} → {target_path}")
                else:
                    print(f"  ✗ Failed: {source_path}")
                return success
            except Exception as e:
                print(f"  ✗ Error moving {source_path}: {e}")
                return False
    
    def move_folder_contents(self, source_folder, target_folder, dry_run=True):
        """Move all contents from source to target folder"""
        print(f"\nMoving contents: {source_folder} → {target_folder}")
        print("-" * 60)
        
        # Check if source exists
        if not self.editor_asset_lib.does_directory_exist(source_folder):
            print(f"✗ Source folder doesn't exist: {source_folder}")
            return False, []
        
        # Get all assets in source folder
        all_assets = self.get_all_assets_in_path(source_folder)
        
        if not all_assets:
            print(f"No assets found in {source_folder}")
            return True, []
        
        print(f"Found {len(all_assets)} assets to move")
        
        moved = []
        failed = []
        
        for asset_data in all_assets:
            source_path = str(asset_data.package_name)
            asset_name = str(asset_data.asset_name)
            
            # Calculate relative path within source folder
            relative_path = source_path.replace(source_folder, '').lstrip('/')
            
            # Build target path
            if relative_path:
                target_path = f"{target_folder}/{relative_path}"
            else:
                target_path = f"{target_folder}/{asset_name}"
            
            success = self.move_asset(source_path, target_path, dry_run)
            
            if success:
                moved.append(source_path)
            else:
                failed.append(source_path)
        
        print(f"\nSummary: {len(moved)} successful, {len(failed)} failed")
        return len(failed) == 0, moved
    
    def reorganize_dbv(self, dry_run=True):
        """Move DBV folder to External/DBV"""
        print("\n" + "="*60)
        print("STEP 1: Moving DBV to External/DBV" + (" (DRY RUN)" if dry_run else ""))
        print("="*60)
        
        return self.move_folder_contents("/Game/DBV", "/Game/External/DBV", dry_run)
    
    def reorganize_maps(self, dry_run=True):
        """Move maps from Courses to Levels/Maps"""
        print("\n" + "="*60)
        print("STEP 2: Moving Maps to Levels/Maps" + (" (DRY RUN)" if dry_run else ""))
        print("="*60)
        
        # Get all assets from Courses folder
        courses_assets = self.get_all_assets_in_path("/Game/Courses")
        
        moved = []
        failed = []
        
        for asset_data in courses_assets:
            source_path = str(asset_data.package_name)
            asset_name = str(asset_data.asset_name)
            asset_class = str(asset_data.asset_class_path.asset_name)
            
            # Only move World/Map assets
            if 'World' in asset_class or 'Map' in asset_class:
                target_path = f"/Game/Levels/Maps/{asset_name}"
                success = self.move_asset(source_path, target_path, dry_run)
                
                if success:
                    moved.append(source_path)
                else:
                    failed.append(source_path)
        
        print(f"\nFound {len(moved) + len(failed)} maps to move")
        print(f"Summary: {len(moved)} successful, {len(failed)} failed")
        
        return len(failed) == 0, moved
    
    def reorganize_topdown_blueprints(self, dry_run=True):
        """Move TopDown blueprints to Core/Blueprints"""
        print("\n" + "="*60)
        print("STEP 3: Moving TopDown Blueprints" + (" (DRY RUN)" if dry_run else ""))
        print("="*60)
        
        topdown_assets = self.get_all_assets_in_path("/Game/TopDown")
        
        moved = []
        failed = []
        
        for asset_data in topdown_assets:
            source_path = str(asset_data.package_name)
            asset_name = str(asset_data.asset_name)
            asset_class = str(asset_data.asset_class_path.asset_name)
            
            # Only move Blueprint assets
            if 'Blueprint' not in asset_class:
                continue
            
            # Classify the blueprint
            asset_name_lower = asset_name.lower()
            
            if 'character' in asset_name_lower or 'player' in asset_name_lower or 'controller' in asset_name_lower:
                target_folder = "/Game/Core/Blueprints/Player"
            elif 'gamemode' in asset_name_lower or 'game' in asset_name_lower:
                target_folder = "/Game/Core/Blueprints/Gameplay"
            else:
                target_folder = "/Game/Core/Blueprints/Gameplay"
            
            target_path = f"{target_folder}/{asset_name}"
            success = self.move_asset(source_path, target_path, dry_run)
            
            if success:
                moved.append(source_path)
            else:
                failed.append(source_path)
        
        print(f"\nFound {len(moved) + len(failed)} blueprints to move")
        print(f"Summary: {len(moved)} successful, {len(failed)} failed")
        
        return len(failed) == 0, moved
    
    def reorganize_input(self, dry_run=True):
        """Move Input assets to UI/VirtualJoystick or Core"""
        print("\n" + "="*60)
        print("STEP 4: Moving Input Assets" + (" (DRY RUN)" if dry_run else ""))
        print("="*60)
        
        input_assets = self.get_all_assets_in_path("/Game/Input")
        
        moved = []
        failed = []
        
        for asset_data in input_assets:
            source_path = str(asset_data.package_name)
            asset_name = str(asset_data.asset_name)
            asset_class = str(asset_data.asset_class_path.asset_name)
            
            # Skip map files
            if 'World' in asset_class or 'Map' in asset_class:
                continue
            
            # Check if it's UI related (Widget, UserWidget, etc.)
            if 'Widget' in asset_class or 'widget' in asset_name.lower() or 'ui' in asset_name.lower():
                target_folder = "/Game/UI/VirtualJoystick"
            else:
                target_folder = "/Game/Core/Blueprints/Player"
            
            target_path = f"{target_folder}/{asset_name}"
            success = self.move_asset(source_path, target_path, dry_run)
            
            if success:
                moved.append(source_path)
            else:
                failed.append(source_path)
        
        print(f"\nFound {len(moved) + len(failed)} input assets to move")
        print(f"Summary: {len(moved)} successful, {len(failed)} failed")
        
        return len(failed) == 0, moved
    
    def execute_reorganization(self, dry_run=True):
        """Execute the full reorganization"""
        print("\n" + "#"*60)
        print("#  SIMPLIFIED CONTENT REORGANIZATION")
        print("#"*60)
        
        if dry_run:
            print("\n⚠️  DRY RUN MODE - No changes will be made")
            print("Set dry_run=False to execute actual moves\n")
        
        results = {}
        
        # Step 1: Move DBV to External
        success, moved = self.reorganize_dbv(dry_run)
        results['dbv'] = {'success': success, 'moved': len(moved)}
        
        # Step 2: Move Maps to Levels
        success, moved = self.reorganize_maps(dry_run)
        results['maps'] = {'success': success, 'moved': len(moved)}
        
        # Step 3: Move TopDown blueprints
        success, moved = self.reorganize_topdown_blueprints(dry_run)
        results['topdown'] = {'success': success, 'moved': len(moved)}
        
        # Step 4: Move Input assets
        success, moved = self.reorganize_input(dry_run)
        results['input'] = {'success': success, 'moved': len(moved)}
        
        # Final summary
        print("\n" + "="*60)
        print("FINAL SUMMARY")
        print("="*60)
        print(f"DBV assets: {results['dbv']['moved']} moved")
        print(f"Maps: {results['maps']['moved']} moved")
        print(f"TopDown blueprints: {results['topdown']['moved']} moved")
        print(f"Input assets: {results['input']['moved']} moved")
        print("\nTotal assets moved: {}".format(sum(r['moved'] for r in results.values())))
        
        print("\n" + "="*60)
        print("FOLDERS TO KEEP AS-IS (Don't move these):")
        print("="*60)
        print("✓ /Game/Characters/ - Your character assets")
        print("✓ /Game/Cursor/ - Cursor assets")
        print("✓ /Game/LevelPrototyping/ - Prototyping tools")
        print("✓ /Game/StarterContent/ - Epic's starter content")
        print("✓ /Game/__ExternalActors__/ - System folder")
        print("✓ /Game/__ExternalObjects__/ - System folder")
        
        if not dry_run:
            print("\n" + "="*60)
            print("NEXT STEPS:")
            print("="*60)
            print("1. Refresh Content Browser")
            print("2. Test your game (Play In Editor)")
            print("3. Save all changes (Ctrl+Shift+S)")
            print("4. Commit to source control")
        
        return results

# Main execution
if __name__ == "__main__":
    reorganizer = SimpleReorganizer()
    
    # Run in dry-run mode first
    print("Running in DRY RUN mode...")
    results = reorganizer.execute_reorganization(dry_run=False)
    
    # To execute for real, uncomment this line:
    # results = reorganizer.execute_reorganization(dry_run=False)
    
    print("\n" + "="*60)
    print("Script completed!")
    print("To execute actual moves, set dry_run=False")
    print("="*60)
