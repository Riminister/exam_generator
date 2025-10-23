# Parse Exam Bank - AI-Powered Exam Generation System

A comprehensive system for analyzing exam bank data and generating new exams using machine learning and chatbot interfaces.

## 🎯 Project Overview

This project aims to create an intelligent system that:
- Analyzes existing exam bank data to understand patterns
- Uses machine learning to generate new, high-quality exam questions
- Provides an interactive chatbot interface for exam creation
- Maintains academic integrity and quality standards

## 📁 Project Structure

```
parse_exam_bank/
├── src/                    # Source code
│   ├── parse.py           # Main exam downloader
│   ├── parse_with_2fa.py  # 2FA authentication
│   └── comprehensive_search.py
├── tests/                  # Test files
│   ├── test_*.py         # Various test scripts
│   └── download_chem281.py
├── docs/                   # Documentation
│   ├── PROJECT_GOALS.md   # Project objectives
│   ├── IMPLEMENTATION_ROADMAP.md
│   └── *.md              # Other documentation
├── exam_downloads/         # Downloaded exam files
│   ├── CHEM281DEC.pdf
│   └── COMM101A_2023-2024.pdf
├── exam_analysis/          # Analysis and preprocessing
│   └── phase1_starter.py  # Data analysis starter
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Git (for version control)
- Chrome browser (for web scraping)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/parse_exam_bank.git
   cd parse_exam_bank
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the exam downloader**
   ```bash
   python src/parse.py
   ```

## 📊 Features

### Current Features
- ✅ **Exam Download**: Automated download from Queen's University QSpace
- ✅ **Microsoft 2FA Support**: Handles Azure AD authentication
- ✅ **Multiple Course Support**: Download exams for various courses
- ✅ **Data Organization**: Structured file management
- ✅ **Analysis Tools**: PDF text extraction and analysis

### Planned Features
- 🤖 **ML Question Generation**: AI-powered exam question creation
- 💬 **Chatbot Interface**: Interactive exam generation
- 📈 **Analytics Dashboard**: Exam pattern analysis
- 🔍 **Quality Assessment**: Automated question validation
- 🌐 **Web Application**: Full-stack exam generation platform

## 🛠️ Development Phases

### Phase 1: Data Foundation (Weeks 1-4)
- PDF text extraction
- Question parsing and classification
- Data cleaning and organization
- Basic pattern recognition

### Phase 2: ML Development (Weeks 5-12)
- Natural language processing
- Question generation models
- Difficulty assessment algorithms
- Quality validation systems

### Phase 3: Web Application (Weeks 13-20)
- Backend API development
- Frontend interface
- Chatbot integration
- User authentication

### Phase 4: Deployment (Weeks 21-24)
- Production deployment
- Performance optimization
- User training and documentation
- Monitoring and maintenance

## 📚 Learning Resources

### Machine Learning
- [Natural Language Processing with Python](https://www.nltk.org/book/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)
- [Fast.ai Practical Deep Learning](https://course.fast.ai/)

### Web Development
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

### Data Science
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Queen's University for providing exam bank access
- Open source community for excellent ML libraries
- Educational institutions for supporting academic innovation

## 📞 Support

If you have any questions or need help:
- Open an issue on GitHub
- Check the documentation in the `docs/` folder
- Review the implementation roadmap

## 🎓 Educational Use

This project is designed for educational purposes. Please respect:
- Academic integrity policies
- Copyright laws
- Terms of service of educational platforms
- Institutional guidelines

---

**Ready to revolutionize exam generation? Let's build the future of educational assessment! 🚀**
