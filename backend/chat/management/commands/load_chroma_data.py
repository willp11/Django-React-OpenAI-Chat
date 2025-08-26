from django.core.management.base import BaseCommand
from chat.chroma import load_documents
import os


class Command(BaseCommand):
    help = 'Load sample documents into Chroma database for RAG testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sample',
            action='store_true',
            help='Load sample data instead of custom documents',
        )
        parser.add_argument(
            '--documents',
            nargs='+',
            type=str,
            help='Custom documents to load into the database',
        )
        parser.add_argument(
            '--file',
            nargs='+',
            type=str,
            help='Path(s) to markdown files to load into the database',
        )

    def read_markdown_file(self, file_path):
        """Read and return the content of a markdown file."""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if not file_path.endswith('.md'):
                self.stdout.write(
                    self.style.WARNING(f'Skipping {file_path}: not a markdown file')
                )
                return None
            
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                return content.strip()
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error reading file {file_path}: {str(e)}')
            )
            return None

    def handle(self, *args, **options):
        if options['sample']:
            # Sample documents about yourself for testing
            sample_docs = [
                "I am a software developer with expertise in Python, Django, and React. "
                "I enjoy building web applications and working with AI technologies. "
                "My favorite programming language is Python because of its readability and extensive ecosystem.",
                
                "I graduated from university with a degree in Computer Science. "
                "During my studies, I focused on web development and machine learning. "
                "I completed several projects including a recommendation system and a web-based task manager.",
                
                "In my free time, I like to contribute to open source projects and learn new technologies. "
                "I'm particularly interested in natural language processing and building chatbots. "
                "I believe AI can greatly enhance user experiences when implemented thoughtfully.",
                
                "I have experience working with various databases including PostgreSQL, MongoDB, and ChromaDB. "
                "I'm comfortable with both SQL and NoSQL approaches depending on the project requirements. "
                "I also have experience with cloud platforms like AWS and deploying applications using Docker.",
                
                "My career goal is to build intelligent applications that solve real-world problems. "
                "I'm passionate about creating software that is not only functional but also user-friendly. "
                "I believe in writing clean, maintainable code and following best practices."
            ]
            
            self.stdout.write(
                self.style.SUCCESS('Loading sample documents into Chroma database...')
            )
            load_documents(sample_docs)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully loaded {len(sample_docs)} sample documents')
            )
            
        elif options['file']:
            file_paths = options['file']
            documents = []
            
            for file_path in file_paths:
                content = self.read_markdown_file(file_path)
                if content:
                    documents.append(content)
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully read: {file_path}')
                    )
            
            if documents:
                self.stdout.write(
                    self.style.SUCCESS(f'Loading {len(documents)} documents from files...')
                )
                load_documents(documents)
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully loaded {len(documents)} documents from files')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('No valid documents found to load')
                )
            
        elif options['documents']:
            custom_docs = options['documents']
            self.stdout.write(
                self.style.SUCCESS(f'Loading {len(custom_docs)} custom documents...')
            )
            load_documents(custom_docs)
            self.stdout.write(
                self.style.SUCCESS('Successfully loaded custom documents')
            )
            
        else:
            self.stdout.write(
                self.style.WARNING(
                    'No documents specified. Use --sample to load sample data, --documents to specify custom documents, or --file to specify markdown file paths.'
                )
            )
            self.stdout.write('Example usage:')
            self.stdout.write('  python manage.py load_chroma_data --sample')
            self.stdout.write('  python manage.py load_chroma_data --documents "Document 1" "Document 2"')
            self.stdout.write('  python manage.py load_chroma_data --file "path/to/file1.md" "path/to/file2.md"')
