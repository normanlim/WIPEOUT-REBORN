"""
Unreal Engine Content Folder Reorganization Script
This script analyzes and reorganizes the Content folder structure for better organization.

Target Structure:
- Core/Blueprints/Player/
- Core/Blueprints/Gameplay/
- Core/Blueprints/Environment/
- UI/VirtualJoystick/
- Levels/Maps/
- External/DBV/

Usage: Run this in Unreal Engine's Python console or as an Editor Utility Script
"""

import unreal
import os
from collections import defaultdict

class ContentReorganizer:
    def __init__(self):
        self.asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
        self.editor_asset_lib = unreal.EditorAssetLibrary()
        
        # Define the new folder structure
        self.target_structure = {
            'Core': [
                'Core/Blueprints/Player',
                'Core/Blueprints/Gameplay',
                'Core/Blueprints/Environment',
                'Core/Materials',
                'Core/Textures'
            ],
            'UI': [
                'UI/VirtualJoystick',
                'UI/Widgets',
                'UI/HUD'
            ],
            'Levels': [
                'Levels/Maps',
                'Levels/Sublevels'
            ],
            'External': [
                'External/DBV'
            ]
        }
        
        # Classification rules for blueprints
        self.bp_classification = {
            'player': ['player', 'character', 'pawn', 'controller'],
            'gameplay': ['platform', 'checkpoint', 'exit', 'bouncy', 'lava'],
            'environment': ['light', 'sky', 'atmosphere', 'fog', 'cloud']
        }
        
    def analyze_current_structure(self):
        """Analyze the current Content folder structure"""
        print("\n" + "="*60)
        print("ANALYZING CURRENT CONTENT STRUCTURE")
        print("="*60)
        
        content_path = "/Game/"
        all_assets = self.asset_registry.get_assets_by_path(content_path, recursive=True)
        
        folder_stats = defaultdict(lambda: {'blueprints': 0, 'maps': 0, 'materials': 0, 'textures': 0, 'other': 0})
        asset_locations = defaultdict(list)
        
        for asset_data in all_assets:
            asset_path = str(asset_data.package_name)
            asset_class = str(asset_data.asset_class_path.asset_name)
            
            # Extract folder from path
            parts = asset_path.replace('/Game/', '').split('/')
            if len(parts) > 1:
                folder = parts[0]
            else:
                folder = 'Root'
            
            # Classify asset
            if 'Blueprint' in asset_class:
                folder_stats[folder]['blueprints'] += 1
                asset_locations['blueprints'].append(asset_path)
            elif 'World' in asset_class or 'Map' in asset_class:
                folder_stats[folder]['maps'] += 1
                asset_locations['maps'].append(asset_path)
            elif 'Material' in asset_class:
                folder_stats[folder]['materials'] += 1
                asset_locations['materials'].append(asset_path)
            elif 'Texture' in asset_class:
                folder_stats[folder]['textures'] += 1
                asset_locations['textures'].append(asset_path)
            else:
                folder_stats[folder]['other'] += 1
        
        # Print current structure
        print("\nCurrent Folder Structure:")
        print("-" * 60)
        for folder, stats in sorted(folder_stats.items()):
            total = sum(stats.values())
            print(f"\n/{folder}/ ({total} assets)")
            for asset_type, count in stats.items():
                if count > 0:
                    print(f"  - {asset_type}: {count}")
        
        print("\n" + "="*60)
        print(f"Total Assets Found: {sum(sum(stats.values()) for stats in folder_stats.values())}")
        print("="*60)
        
        return asset_locations, folder_stats
    
    def create_folder_structure(self):
        """Create the new folder structure"""
        print("\n" + "="*60)
        print("CREATING NEW FOLDER STRUCTURE")
        print("="*60)
        
        created_folders = []
        
        for category, folders in self.target_structure.items():
            for folder in folders:
                game_path = f"/Game/{folder}"
                if self.editor_asset_lib.does_directory_exist(game_path):
                    print(f"✓ Folder exists: {game_path}")
                else:
                    success = self.editor_asset_lib.make_directory(game_path)
                    if success:
                        print(f"✓ Created: {game_path}")
                        created_folders.append(game_path)
                    else:
                        print(f"✗ Failed to create: {game_path}")
        
        return created_folders
    
    def classify_blueprint(self, asset_name):
        """Classify a blueprint based on its name"""
        asset_name_lower = asset_name.lower()
        
        for category, keywords in self.bp_classification.items():
            if any(keyword in asset_name_lower for keyword in keywords):
                return category
        
        return 'gameplay'  # Default category
    
    def move_blueprints(self, dry_run=True):
        """Move blueprints to their appropriate folders"""
        print("\n" + "="*60)
        print("REORGANIZING BLUEPRINTS" + (" (DRY RUN)" if dry_run else ""))
        print("="*60)
        
        # Get all blueprint assets
        all_assets = self.asset_registry.get_assets_by_class(unreal.Name("Blueprint"), recursive=True)
        
        moves = []
        errors = []
        
        for asset_data in all_assets:
            asset_path = str(asset_data.package_name)
            asset_name = str(asset_data.asset_name)
            
            # Skip if already in External/DBV
            if '/DBV/' in asset_path or '/External/' in asset_path:
                continue
            
            # Skip if already in the target structure
            if any(target in asset_path for target in ['Core/Blueprints', 'UI/', 'Levels/']):
                continue
            
            # Classify the blueprint
            category = self.classify_blueprint(asset_name)
            
            # Determine target path
            if category == 'player':
                target_folder = '/Game/Core/Blueprints/Player'
            elif category == 'gameplay':
                target_folder = '/Game/Core/Blueprints/Gameplay'
            elif category == 'environment':
                target_folder = '/Game/Core/Blueprints/Environment'
            else:
                target_folder = '/Game/Core/Blueprints/Gameplay'
            
            target_path = f"{target_folder}/{asset_name}"
            
            moves.append({
                'source': asset_path,
                'target': target_path,
                'category': category
            })
            
            print(f"\n{asset_name}")
            print(f"  Category: {category}")
            print(f"  From: {asset_path}")
            print(f"  To:   {target_path}")
            
            if not dry_run:
                success = self.editor_asset_lib.rename_asset(asset_path, target_path)
                if not success:
                    errors.append(f"Failed to move {asset_path} to {target_path}")
                    print(f"  ✗ FAILED")
                else:
                    print(f"  ✓ MOVED")
        
        return moves, errors
    
    def move_dbv_to_external(self, dry_run=True):
        """Move DBV folder contents to External/DBV"""
        print("\n" + "="*60)
        print("MOVING DBV TO EXTERNAL" + (" (DRY RUN)" if dry_run else ""))
        print("="*60)
        
        dbv_path = "/Game/DBV"
        target_path = "/Game/External/DBV"
        
        if not self.editor_asset_lib.does_directory_exist(dbv_path):
            print(f"✗ DBV folder not found at {dbv_path}")
            return False
        
        print(f"\nMoving: {dbv_path} -> {target_path}")
        
        if not dry_run:
            # Get all assets in DBV folder
            all_assets = self.asset_registry.get_assets_by_path(dbv_path, recursive=True)
            
            for asset_data in all_assets:
                asset_path = str(asset_data.package_name)
                asset_name = str(asset_data.asset_name)
                
                # Calculate relative path within DBV
                relative_path = asset_path.replace(dbv_path, '').lstrip('/')
                new_path = f"{target_path}/{relative_path}"
                
                print(f"  Moving: {asset_name}")
                success = self.editor_asset_lib.rename_asset(asset_path, new_path)
                if success:
                    print(f"    ✓ Moved to {new_path}")
                else:
                    print(f"    ✗ Failed")
        else:
            print("  (Would move all DBV assets to External/DBV)")
        
        return True
    
    def move_maps_to_levels(self, dry_run=True):
        """Move map files to Levels/Maps"""
        print("\n" + "="*60)
        print("ORGANIZING MAPS" + (" (DRY RUN)" if dry_run else ""))
        print("="*60)
        
        # Get all map/level assets
        all_assets = self.asset_registry.get_assets_by_class(unreal.Name("World"), recursive=True)
        
        moves = []
        
        for asset_data in all_assets:
            asset_path = str(asset_data.package_name)
            asset_name = str(asset_data.asset_name)
            
            # Skip if already in Levels folder
            if '/Levels/' in asset_path:
                continue
            
            target_path = f"/Game/Levels/Maps/{asset_name}"
            
            moves.append({
                'source': asset_path,
                'target': target_path
            })
            
            print(f"\n{asset_name}")
            print(f"  From: {asset_path}")
            print(f"  To:   {target_path}")
            
            if not dry_run:
                success = self.editor_asset_lib.rename_asset(asset_path, target_path)
                if success:
                    print(f"  ✓ MOVED")
                else:
                    print(f"  ✗ FAILED")
        
        return moves
    
    def generate_report(self):
        """Generate a final reorganization report"""
        print("\n" + "="*60)
        print("REORGANIZATION COMPLETE - FINAL STRUCTURE")
        print("="*60)
        
        self.analyze_current_structure()
        
        print("\n" + "="*60)
        print("RECOMMENDATIONS")
        print("="*60)
        print("\n1. Review all moved assets in Unreal Editor")
        print("2. Fix any broken references in blueprints")
        print("3. Update any hard-coded asset paths in code")
        print("4. Save all modified assets")
        print("5. Consider creating README files in each folder")
        print("\nNext Steps:")
        print("- Core/Blueprints: Contains all gameplay blueprints organized by type")
        print("- UI/VirtualJoystick: Ready for UI widget blueprints")
        print("- Levels/Maps: Contains all map files")
        print("- External/DBV: Contains downloaded DBV assets")
    
    def execute_full_reorganization(self, dry_run=True):
        """Execute the complete reorganization process"""
        print("\n" + "#"*60)
        print("#" + " "*58 + "#")
        print("#  UNREAL ENGINE CONTENT FOLDER REORGANIZATION" + " "*13 + "#")
        print("#" + " "*58 + "#")
        print("#"*60)
        
        if dry_run:
            print("\n⚠️  DRY RUN MODE - No changes will be made")
            print("Set dry_run=False to execute actual moves\n")
        
        # Step 1: Analyze current structure
        asset_locations, folder_stats = self.analyze_current_structure()
        
        # Step 2: Create new folder structure
        created_folders = self.create_folder_structure()
        
        # Step 3: Move blueprints
        bp_moves, bp_errors = self.move_blueprints(dry_run)
        
        # Step 4: Move DBV to External
        self.move_dbv_to_external(dry_run)
        
        # Step 5: Move maps to Levels
        map_moves = self.move_maps_to_levels(dry_run)
        
        # Step 6: Generate report
        if not dry_run:
            self.generate_report()
        
        # Summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Blueprints to reorganize: {len(bp_moves)}")
        print(f"Maps to move: {len(map_moves)}")
        print(f"Folders created: {len(created_folders)}")
        if bp_errors:
            print(f"Errors encountered: {len(bp_errors)}")
        
        return {
            'blueprint_moves': bp_moves,
            'map_moves': map_moves,
            'created_folders': created_folders,
            'errors': bp_errors
        }


# Main execution
if __name__ == "__main__":
    reorganizer = ContentReorganizer()
    
    # First run in dry-run mode to preview changes
    print("Running in DRY RUN mode to preview changes...")
    results = reorganizer.execute_full_reorganization(dry_run=True)
    
    # Uncomment the line below to execute actual reorganization
    # results = reorganizer.execute_full_reorganization(dry_run=False)
    
    print("\n" + "="*60)
    print("Script execution completed!")
    print("To execute the actual reorganization, set dry_run=False")
    print("="*60)
