#!/usr/bin/env python3
"""
Reorganize Project - Clean Structure
Creates new folder structure and moves files appropriately
"""

import shutil
from pathlib import Path
from typing import List, Tuple


class ProjectReorganizer:
    """Reorganize project into clean structure"""
    
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.moves: List[Tuple[Path, Path]] = []
        self.created_dirs: List[Path] = []
        
    def create_structure(self):
        """Create new folder structure"""
        new_structure = [
            'exam_generation',
            'text_extraction',
            'graph_extraction',
            'data_cleaning',
            'exam_generation/openai',
            'exam_generation/assembly',
            'text_extraction/pdf_processing',
            'text_extraction/question_parsing',
            'graph_extraction/analysis',
            'graph_extraction/recreation',
            'data_cleaning/cleaners',
            'data_cleaning/validators',
            'outputs/generated_graphs',
            'outputs/generated_exams',
            'outputs/analysis_results',
        ]
        
        for dir_path in new_structure:
            path = Path(dir_path)
            if not self.dry_run:
                path.mkdir(parents=True, exist_ok=True)
            self.created_dirs.append(path)
            print(f"  📁 {dir_path}")
    
    def organize_files(self):
        """Organize files into new structure"""
        
        # ========== EXAM GENERATION ==========
        exam_gen_files = {
            'openai_question_generator.py': 'exam_generation/openai/',
            'generate_exam_from_data.py': 'exam_generation/assembly/',
        }
        
        # ========== TEXT EXTRACTION ==========
        text_extraction_files = {
            'extract_text_from_pdfs.py': 'text_extraction/pdf_processing/',
            'parse_questions_from_text.py': 'text_extraction/question_parsing/',
            'extract_cover_page_metadata.py': 'text_extraction/pdf_processing/',
            'detect_question_types.py': 'text_extraction/question_parsing/',
        }
        
        # Text extraction modules
        text_extraction_modules = {
            'exam_analysis/text_extractor.py': 'text_extraction/pdf_processing/',
            'exam_analysis/cover_page_parser.py': 'text_extraction/pdf_processing/',
            'exam_analysis/ocr_context_selector.py': 'text_extraction/pdf_processing/',
            'exam_analysis/question_type_detector.py': 'text_extraction/question_parsing/',
            'exam_analysis/sub_question_detector.py': 'text_extraction/question_parsing/',
            'exam_analysis/detect_sub_questions.py': 'text_extraction/question_parsing/',
            'exam_analysis/translation_detector.py': 'text_extraction/pdf_processing/',
        }
        
        # ========== GRAPH EXTRACTION ==========
        graph_extraction_files = {
            'exam_analysis/graph_analyzer.py': 'graph_extraction/analysis/',
            'exam_analysis/graph_recreator.py': 'graph_extraction/recreation/',
            'exam_analysis/graph_generator.py': 'graph_extraction/recreation/',
            'exam_analysis/openai_question_analyzer.py': 'graph_extraction/analysis/',
            'integrate_graph_analysis.py': 'graph_extraction/',
            'integrate_openai_analysis.py': 'graph_extraction/analysis/',
        }
        
        # ========== DATA CLEANING ==========
        data_cleaning_files = {
            'exam_analysis/data_cleaner.py': 'data_cleaning/cleaners/',
            'exam_analysis/difficulty_calculator.py': 'data_cleaning/validators/',
            'exam_analysis/calculate_difficulty.py': 'data_cleaning/validators/',
            'exam_analysis/run_cleaning.py': 'data_cleaning/',
        }
        
        # ========== SCRIPTS ==========
        script_files = {
            'setup_openai.py': 'scripts/',
            'detect_translation_issues.py': 'scripts/',
            'run_model_complete.py': 'scripts/',
        }
        
        # ========== TESTS ==========
        test_files = {
            'test_improved_model.py': 'tests/',
        }
        
        # Combine all mappings
        all_moves = {
            **exam_gen_files,
            **text_extraction_files,
            **text_extraction_modules,
            **graph_extraction_files,
            **data_cleaning_files,
            **script_files,
            **test_files,
        }
        
        # Create move list
        for src_file, dest_dir in all_moves.items():
            src = Path(src_file)
            if src.exists():
                dest = Path(dest_dir) / src.name
                self.moves.append((src, dest))
            else:
                # Check if it's a module that might not exist
                if 'detect_sub_questions.py' in src_file:
                    # This might be a duplicate, skip if doesn't exist
                    pass
    
    def organize_documentation(self):
        """Move documentation to appropriate locations"""
        doc_moves = {
            # Exam generation docs
            'EXAM_GENERATION_STATUS.md': 'exam_generation/',
            'OPENAI_SETUP_GUIDE.md': 'exam_generation/openai/',
            'OPENAI_GRAPH_INTEGRATION_GUIDE.md': 'exam_generation/openai/',
            'QUICK_START_OPENAI.md': 'exam_generation/openai/',
            
            # Text extraction docs
            'OCR_RE_EXTRACTION_GUIDE.md': 'text_extraction/pdf_processing/',
            'SUB_QUESTION_GUIDE.md': 'text_extraction/question_parsing/',
            'DIFFICULTY_SCORE_GUIDE.md': 'text_extraction/question_parsing/',
            
            # Data cleaning docs
            'exam_analysis/DATA_CLEANING_GUIDE.md': 'data_cleaning/',
            
            # General docs
            'COMPLETE_WORKFLOW.md': 'docs/guides/',
            'WORKFLOW_ORDER.md': 'docs/guides/',
            'FOLDER_STRUCTURE_GUIDE.md': 'docs/guides/',
            'FEATURES_SUMMARY.md': 'docs/guides/',
            'STRATEGIC_NEXT_STEPS.md': 'docs/guides/',
            'IMPROVE_R2_SCORE.md': 'docs/guides/',
            'BUILD_FIRST_MODEL_GUIDE.md': 'docs/guides/',
            'QUICK_START_MODEL.md': 'docs/guides/',
        }
        
        for src_file, dest_dir in doc_moves.items():
            src = Path(src_file)
            if src.exists():
                dest = Path(dest_dir) / src.name
                self.moves.append((src, dest))
    
    def create_init_files(self):
        """Create __init__.py files for Python packages"""
        init_files = [
            'exam_generation/__init__.py',
            'exam_generation/openai/__init__.py',
            'exam_generation/assembly/__init__.py',
            'text_extraction/__init__.py',
            'text_extraction/pdf_processing/__init__.py',
            'text_extraction/question_parsing/__init__.py',
            'graph_extraction/__init__.py',
            'graph_extraction/analysis/__init__.py',
            'graph_extraction/recreation/__init__.py',
            'data_cleaning/__init__.py',
            'data_cleaning/cleaners/__init__.py',
            'data_cleaning/validators/__init__.py',
        ]
        
        for init_file in init_files:
            path = Path(init_file)
            if not self.dry_run:
                path.parent.mkdir(parents=True, exist_ok=True)
                if not path.exists():
                    path.write_text('# Package init\n')
            print(f"  📝 {init_file}")
    
    def execute_moves(self):
        """Execute all file moves"""
        print()
        print("Moving files...")
        print()
        
        for src, dest in self.moves:
            try:
                if dest.exists():
                    print(f"⚠️  Skipping {src} - {dest} already exists")
                else:
                    if not self.dry_run:
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(src), str(dest))
                    print(f"✅ {src} → {dest}")
            except Exception as e:
                print(f"❌ Error moving {src}: {e}")
    
    def update_imports_info(self):
        """Create file with import path updates needed"""
        info = """# Import Path Updates Needed

After reorganization, some imports may need to be updated:

## Text Extraction
- `from exam_analysis.text_extractor import ...` 
  → `from text_extraction.pdf_processing.text_extractor import ...`

## Graph Extraction  
- `from exam_analysis.graph_analyzer import ...`
  → `from graph_extraction.analysis.graph_analyzer import ...`

## Data Cleaning
- `from exam_analysis.data_cleaner import ...`
  → `from data_cleaning.cleaners.data_cleaner import ...`

## Exam Generation
- `from openai_question_generator import ...`
  → `from exam_generation.openai.openai_question_generator import ...`

Run tests after reorganization to identify any import issues.
"""
        
        path = Path('REORGANIZATION_NOTES.md')
        if not self.dry_run:
            path.write_text(info)
        print(f"  📝 Created REORGANIZATION_NOTES.md")
    
    def reorganize(self):
        """Main reorganization function"""
        print("=" * 70)
        print("PROJECT REORGANIZATION")
        print("=" * 70)
        print()
        
        if self.dry_run:
            print("🔍 DRY RUN MODE - No files will be moved")
            print()
        
        # Step 1: Create structure
        print("Step 1: Creating folder structure...")
        self.create_structure()
        print()
        
        # Step 2: Create __init__.py files
        print("Step 2: Creating Python package files...")
        self.create_init_files()
        print()
        
        # Step 3: Organize files
        print("Step 3: Organizing files...")
        self.organize_files()
        self.organize_documentation()
        print(f"  Found {len(self.moves)} files to move")
        print()
        
        # Step 4: Execute moves
        if self.moves:
            self.execute_moves()
        
        # Step 5: Create notes
        print()
        print("Step 4: Creating reorganization notes...")
        self.update_imports_info()
        
        # Summary
        print()
        print("=" * 70)
        print("REORGANIZATION SUMMARY")
        print("=" * 70)
        print(f"Directories created: {len(self.created_dirs)}")
        print(f"Files moved: {len(self.moves)}")
        print()
        
        if self.dry_run:
            print("Run without --dry-run to execute changes")
        else:
            print("✅ Reorganization complete!")
            print()
            print("⚠️  IMPORTANT: Update imports in your code:")
            print("   See REORGANIZATION_NOTES.md for details")
            print()
            print("Next steps:")
            print("1. Review moved files")
            print("2. Update imports in code")
            print("3. Run tests: python tests/test_comprehensive.py")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Reorganize project structure")
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be done without making changes')
    
    args = parser.parse_args()
    
    reorganizer = ProjectReorganizer(dry_run=args.dry_run)
    reorganizer.reorganize()

