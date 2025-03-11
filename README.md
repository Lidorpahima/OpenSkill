# ✨ Welcome to **UPSKILL** 🚀

UPSKILL is an AI-powered personalized learning platform designed to help users achieve their learning goals efficiently and effectively. The platform guides users through a journey of self-improvement, from career path selection to skill acquisition.

<img src="Screenshot/upskilllogo.png" alt="UPSKILL Banner" width="300"/>

## 🔍 Key Features:

- 🤖 **AI-Powered Career Guidance**: Smart chatbot to help users discover suitable career paths based on their interests and skills
- 📋 **Personalized Learning Goals**: Create and track progress on customized learning objectives
- 📊 **Career Path Planning**: Clear recommended learning paths to help users achieve their professional goals
- 📝 **Progress Tracking**: Visual indicators to monitor advancement toward goals
## ⚙️ Technologies Used:

- 🐍 **Backend**: FastAPI (Python) microservices architecture
- 🗃️ **Database**: PostgreSQL for complex data + Redis for caching & performance
- 🔐 **Authentication**: OAuth2 + JWT for secure access control
- 🔗 **Real-Time Communication**: Integration with AI models for intelligent chat interactions
- 📦 **Containerization**: Docker + Docker Compose for easy deployment
- ☁️ **Deployment**: Ready for cloud infrastructure deployment

## 📊 Microservices Architecture:

UPSKILL is built using a microservices approach, ensuring scalability and flexibility. Each service handles specific responsibilities:

- 👤 **User Service**: Handles registration, login, and user management
- 📚 **Learning Service**: Manages learning goals, content, and progress tracking
- 📝 **Assessment Service**: Provides AI-powered career guidance and evaluations
- 🔒 **Authentication Service**: Manages user authentication and security
- 🌐 **Gateway Service**: Coordinates communication between services

## 🚀 Quick Start:

```bash
# Clone the repository
git clone https://github.com/your-repo/upskill.git

# Navigate to the project directory
cd upskill

# Start the services using Docker Compose
docker-compose up --build
```

## 🔧 Project Structure

```
upskill/
├── services/
│   ├── user_service/         # User registration and management
│   ├── learning_service/     # Learning goals and progress tracking
│   ├── assessment_service/   # AI chat and career recommendations
│   ├── authentication_service/ # Authentication and security
│   ├── gateway_service/      # API gateway for service communication
│   └── frontend/             # Web interface
├── docker-compose.yml        # Service configuration
└── README.md                 # Project documentation
```
## 🖼️ Screenshots

### AI Chat Interface

<img src="Screenshot/AI_Chat.png" alt="AI Chat" width="400"/>

### Learning Goals Dashboard
<img src="Screenshot/Learning_Goals.png" alt="Learning Goals" width="400"/>

### Career Path Recommendations
<img src="Screenshot/Career_Path.png" alt="Career Path" width="400"/>

### Career Recommendations
<img src="Screenshot/Career_Recoommendations.png" alt="Career Recommendations" width="400"/>

## 📞 Contact:

For any inquiries or feedback, feel free to reach out at [lidorpahima28@gmail.com](mailto:lidorpahima28@gmail.com) ✉️

**Let's build the future of learning together! 🚀🌍**
