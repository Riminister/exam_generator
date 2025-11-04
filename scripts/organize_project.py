#!/usr/bin/env python3
"""
Organize and Clean Up Project Structure
Moves files to proper directories and removes duplicates
"""

import shutil
from pathlib import Path
from typing import List, Dict


class ProjectOrganizer:
    """Organize project files into proper structure"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.moves = []
        self.deletes = []
        
    def organize(self):
        """Main organization function"""
        print("=" * 70)
        print("PROJECT ORGANIZATION")
        print("=" * 70)
        print()
        
        if self.dry_run:
            print("🔍 DRY RUN MODE - No files will be moved")
            print()
        
        # Define file organization rules
        self._organize_python_scripts()
        self._organize_documentation()
        self._remove_duplicates()
        self._cleanup_temp_files()
        
        # Execute moves
        if not self.dry_run:
            self._execute_moves()
            self._execute_deletes()
        
        self._print_summary()
    
    def _organize_python_scripts(self):
        """Organize Python scripts"""
        # Scripts that should be in scripts/ directory
        scripts_to_move = {
            'setup_openai.py': 'scripts/',
            'integrate_openai_analysis.py': 'scripts/',
            'integrate_graph_analysis.py': 'scripts/',
            'generate_exam_from_data.py': 'scripts/',
            'detect_question_types.py': 'scripts/',
            'detect_translation_issues.py': 'scripts/',
            'run_model_complete.py': 'scripts/',
            'test_improved_model.py': 'tests/',
        }
        
        # Main pipeline scripts stay in root
        # (extract_text_from_pdfs.py, parse_questions_from_text.py, etc.)
        
        for file, dest_dir in scripts_to_move.items():
            src = Path(file)
            if src.exists():
                dest = Path(dest_dir) / file
                self.moves.append((src, dest))
    
    def _organize_documentation(self):
        """Organize documentation files"""
        # Move guides to docs/guides/
        guides_to_move = {
            'BUILD_FIRST_MODEL_GUIDE.md': 'docs/guides/',
            'COMPLETE_WORKFLOW.md': 'docs/guides/',
            'DIFFICULTY_SCORE_GUIDE.md': 'docs/guides/',
            'EXAM_GENERATION_STATUS.md': 'docs/guides/',
            'FOLDER_STRUCTURE_GUIDE.md': 'docs/guides/',
            'IMPROVE_R2_SCORE.md': 'docs/guides/',
            'OCR_RE_EXTRACTION_GUIDE.md': 'docs/guides/',
            'OPENAI_GRAPH_INTEGRATION_GUIDE.md': 'docs/guides/',
            'OPENAI_SETUP_GUIDE.md': 'docs/guides/',
            'QUICK_START_MODEL.md': 'docs/guides/',
            'QUICK_START_OPENAI.md': 'docs/guides/',
            'STRATEGIC_NEXT_STEPS.md': 'docs/guides/',
            'SUB_QUESTION_GUIDE.md': 'docs/guides/',
            'WORKFLOW_ORDER.md': 'docs/guides/',
            'FEATURES_SUMMARY.md': 'docs/guides/',
        }
        
        for file, dest_dir in guides_to_move.items():
            src = Path(file)
            if src.exists():
                dest = Path(dest_dir) / file
                self.moves.append((src, dest))
    
    def _remove_duplicates(self):
        """Remove duplicate files"""
        duplicates = [
            # Check for duplicate sub-question detectors
            ('exam_analysis/detect_sub_questions.py', 'exam_analysis/sub_question_detector.py'),
            # Keep the more complete one
        ]
        
        for file1, file2 in duplicates:
            path1 = Path(file1)
            path2 = Path(file2)
            
            if path1.exists() and path2.exists():
                # Keep the one with more content
                if path1.stat().st_size >= path2.stat().st_size:
                    self.deletes.append(path2)
                else:
                    self.deletes.append(path1)
    
    def _cleanup_temp_files(self):
        """Remove temporary files"""
        temp_files = [
            'output.txt',
            'generated_questions_openai.json',  # Move to outputs/ instead?
        ]
        
        for file in temp_files:
            path = Path(file)
            if path.exists():
                # Move to outputs/ instead of deleting
                dest = Path('outputs') / file
                self.moves.append((path, dest))
    
    def _execute_moves(self):
        """Execute file moves"""
        for src, dest in self.moves:
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dest.exists():
                    print(f"⚠️  Skipping {src} - {dest} already exists")
                else:
                    shutil.move(str(src), str(dest))
                    print(f"✅ Moved: {src} → {dest}")
            except Exception as e:
                print(f"❌ Error moving {src}: {e}")
    
    def _execute_deletes(self):
        """Execute file deletions"""
        for path in self.deletes:
            try:
                path.unlink()
                print(f"🗑️  Deleted: {path}")
            except Exception as e:
                print(f"❌ Error deleting {path}: {e}")
    
    def _print_summary(self):
        """Print organization summary"""
        print()
        print("=" * 70)
        print("ORGANIZATION SUMMARY")
        print("=" * 70)
        print(f"Files to move: {len(self.moves)}")
        print(f"Files to delete: {len(self.deletes)}")
        print()
        
        if self.dry_run:
            print("Run without --dry-run to execute changes")
        else:
            print("✅ Organization complete!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Organize project files")
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    
    args = parser.parse_args()
    
    organizer = ProjectOrganizer(dry_run=args.dry_run)
    organizer.organize()

