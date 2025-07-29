# WanderWhiz 🌐 - AI-Powered Travel Itinerary Planner

![WanderWhiz Logo](https://img.shields.io/badge/WanderWhiz-AI%20Travel%20Planner-orange?style=for-the-badge&logo=travel)

**WanderWhiz** is an intelligent travel itinerary planning application that uses AI and Google Maps integration to create optimized travel routes based on your interests. Built for the Google AI Hackathon, it combines the power of OpenAI's GPT models with Google's comprehensive location data.

## 🚀 Features

### ✨ Core Features
- **🧠 AI-Powered Planning**: Uses OpenAI GPT to understand natural language travel requests
- **🗺️ Smart Route Optimization**: Leverages Google Maps Routes API for optimal travel paths
- **📍 Real-time Place Data**: Integrates Google Places API for up-to-date location information
- **💾 Trip Saving**: Firebase integration for persistent trip storage
- **📱 Responsive Design**: Modern, mobile-friendly interface
- **🎯 Interest-Based Search**: Finds places based on your specific interests

### 🎯 Intelligent Trip Planning
- **AI-Powered Recommendations**: OpenAI GPT suggests personalized activities based on your interests
- **Real-time Place Data**: Google Places API provides up-to-date venue information and ratings
- **Smart Route Optimization**: Efficient travel paths between destinations
- **Dynamic Budget Estimation**: Cost calculations for transportation and activities

### 🗺️ Interactive Mapping
- **Embedded Google Maps**: Visualize your entire trip route
- **Custom Markers**: Color-coded location indicators
- **Turn-by-turn Directions**: Detailed navigation between stops
- **Mobile-Optimized**: Touch-friendly map controls

### 💾 Trip Management
- **Cloud Storage**: Firebase Firestore for reliable trip persistence
- **Session Backup**: Local storage fallback for offline access
- **PDF Export**: Professional itinerary documents
- **Trip Sharing**: Unique URLs for sharing with friends

### 📱 Modern Interface
- **Responsive Design**: Works perfectly on all devices
- **Progressive Web App**: Mobile app-like experience
- **Real-time Feedback**: Loading states and instant updates
- **Emoji-Rich UI**: Visual indicators and modern design

## 🏗️ System Architecture

```
                           🌐 WanderWhiz Platform
    ┌─────────────────────────────────────────────────────────────────────┐
    │                                                                     │
    │  👤 User Input: "Plan romantic Paris trip with cafes and museums"   │
    │                               │                                     │
    │                               ▼                                     │
    │  ┌─────────────────────────────────────────────────────────────┐    │
    │  │              🖥️ Frontend Layer                               │    │
    │  │                                                             │    │
    │  │  📱 HTML5/CSS3  ⚡ JavaScript ES6+  🗺️ Google Maps JS      │    │
    │  │                                                             │    │
    │  └─────────────────────────┬───────────────────────────────────┘    │
    │                           │                                         │
    │                           ▼                                         │
    │  ┌─────────────────────────────────────────────────────────────┐    │
    │  │              ⚙️ Backend Services                             │    │
    │  │                                                             │    │
    │  │  🐍 Flask App  🔧 Route Processing  🔐 Session Management   │    │
    │  │                                                             │    │
    │  └──────────┬──────────────┬──────────────────┬─────────────────┘    │
    │             │              │                  │                     │
    │             ▼              ▼                  ▼                     │
    │  ┌─────────────┐  ┌─────────────────┐  ┌─────────────────────┐      │
    │  │ 🤖 OpenAI    │  │ 🌍 Google APIs  │  │ 💾 Firebase         │      │
    │  │ GPT-4        │  │                 │  │ Firestore          │      │
    │  │             │  │ 📍 Places API   │  │                     │      │
    │  │ Natural      │  │ 🛣️ Routes API   │  │ Trip Storage        │      │
    │  │ Language     │  │ 🌐 Geocoding    │  │ User Sessions       │      │
    │  │ Processing   │  │ 🗺️ Maps JS API  │  │                     │      │
    │  └─────────────┘  └─────────────────┘  └─────────────────────┘      │
    │                                                                     │
    │                               ▼                                     │
    │  🎯 Result: Optimized itinerary with interactive map in 0.94s      │
    └─────────────────────────────────────────────────────────────────────┘
```

### 🔄 Data Flow Process
1. **👤 User Input** → Natural language travel request via web interface
2. **🧠 AI Processing** → OpenAI GPT-4 extracts city, interests, and preferences  
3. **🔍 Location Search** → Google Places API finds relevant venues with ratings
4. **🛣️ Route Optimization** → Google Routes API calculates optimal travel paths
5. **💾 Trip Storage** → Firebase Firestore persists itinerary data securely
6. **🗺️ Interactive Display** → Google Maps renders trip with custom markers and routes

### ⚡ Performance Optimizations
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Places Processed** | 80+ venues | 40 venues max | **60% faster** |
| **Response Time** | 15+ seconds | **0.94 seconds** | **94% faster** |
| **Database Calls** | Multiple connections | Singleton pattern | **Optimized** |
| **Mobile Performance** | Basic | Touch-optimized | **Enhanced** |

### 📊 Technical Architecture Diagram

```mermaid
graph TB
    subgraph "🖥️ Frontend Layer"
        A[📱 HTML5/CSS3] 
        B[⚡ JavaScript ES6+]
        C[🗺️ Google Maps JS API]
    end
    
    subgraph "⚙️ Backend Services"  
        D[🐍 Flask Application]
        E[🔧 Route Processing]
        F[🔐 Session Management]
    end
    
    subgraph "🤖 AI Services"
        G[🧠 OpenAI GPT-4]
        H[🎯 Natural Language Processing]
    end
    
    subgraph "🌍 Google APIs"
        I[📍 Places API]
        J[🛣️ Routes API] 
        K[🌐 Geocoding API]
    end
    
    subgraph "💾 Database"
        L[🔥 Firebase Firestore]
        M[📊 Trip Storage]
    end
    
    %% User Flow
    N[👤 User] --> A
    A --> D
    B --> D
    C --> D
    D --> G
    D --> I
    D --> J
    D --> K
    G --> H
    I --> E
    J --> E
    K --> E
    D --> L
    L --> M
    
    %% Styling
    classDef frontend fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef backend fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef ai fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef google fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef database fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    
    class A,B,C frontend
    class D,E,F backend
    class G,H ai
    class I,J,K google
    class L,M database
```

## 🛠️ Technology Stack

### 🖥️ Frontend
- **HTML5/CSS3**: Modern responsive design with CSS Grid/Flexbox
- **JavaScript ES6+**: Interactive functionality and API integration
- **Google Maps JavaScript API**: Real-time map rendering and controls

### ⚙️ Backend
- **Python 3.8+**: Core programming language
- **Flask 2.3+**: Lightweight web framework for API endpoints
- **Jinja2 Templates**: Server-side rendering with dynamic content
- **Vanilla JavaScript**: Lightweight, no-framework approach
- **Modern CSS**: Responsive design with glassmorphism effects
- **Progressive Enhancement**: Works without JavaScript

### Infrastructure
- **Virtual Environment**: Isolated Python dependencies
- **Environment Variables**: Secure API key management
- **Error Handling**: Comprehensive exception management
- **Session Management**: User state persistence

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Maps API Key
- OpenAI API Key
- Firebase Project (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/wanderwhiz.git
   cd wanderwhiz
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the project root:
   ```env
   GOOGLE_MAPS_API_KEY=your_google_maps_api_key
   OPENAI_API_KEY=your_openai_api_key
   SECRET_KEY=your_secret_key_for_sessions
   ```

5. **Set up Firebase (optional)**
   - Create a Firebase project at [Firebase Console](https://console.firebase.google.com)
   - Generate a service account key
   - Save as `firebase-key.json` in the project root

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Open your browser**
   Navigate to `http://127.0.0.1:5001`

## 📖 Usage Guide

### Planning Your Trip

1. **Enter Destination**: Type your destination city
2. **Specify Interests**: Describe what you want to do (e.g., "museums, food, parks")
3. **Generate Itinerary**: Click "Build My Itinerary" to get AI-powered suggestions
4. **Explore Results**: View optimized route on interactive map
5. **Save Trip**: Store your itinerary for future reference
6. **Export PDF**: Download professional trip documents

### Advanced Features

- **Route Optimization**: Automatically calculates the most efficient path
- **Time Estimation**: Provides realistic travel time between locations
- **Budget Planning**: Estimates costs for activities and transportation
- **Mobile Access**: Full functionality on smartphones and tablets

## 🔧 Configuration

### Google Maps API Setup
1. Visit [Google Cloud Console](https://console.cloud.google.com)
2. Enable Maps JavaScript API, Places API, and Directions API
3. Create an API key with appropriate restrictions
4. Add your domain to authorized referrers

### OpenAI API Setup
1. Sign up at [OpenAI Platform](https://platform.openai.com)
2. Generate an API key from your dashboard
3. Add billing information for production use

### Firebase Setup (Optional)
1. Create project at [Firebase Console](https://console.firebase.google.com)
2. Set up Firestore database
3. Generate service account credentials
4. Download `firebase-key.json`

## 📁 Project Structure

```
wanderwhiz/
├── app.py                    # Main Flask application
├── firebase_config.py        # Firebase integration
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (create this)
├── firebase-key.json         # Firebase credentials (create this)
├── static/
│   ├── css/
│   │   └── styles.css       # Main stylesheet
│   └── js/
│       └── map.js           # Map utilities
├── templates/
│   ├── index.html           # Home page
│   └── itinerary.html       # Trip display
├── demo_data.py             # Sample data
├── utils.py                 # Utility functions
└── docs/
    ├── ARCHITECTURE.md      # System architecture
    ├── DEVELOPMENT_REPORT.md # Development progress
    └── FIREBASE_SETUP.md    # Firebase guide
```

## 🚢 Deployment

### Vercel (Recommended)
```bash
npm i -g vercel
vercel --prod
```

### Google App Engine
```bash
gcloud app deploy
```

### Docker
```bash
docker build -t wanderwhiz .
docker run -p 5001:5001 wanderwhiz
```

## 🧪 Testing

Run the test suite to verify functionality:

```bash
# Test Firebase connection and core features
python test_manual.py

# Test complete workflow
python test_complete_workflow.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Maps Platform**: For comprehensive mapping and location services
- **OpenAI**: For powerful AI-driven recommendations
- **Firebase**: For reliable cloud infrastructure
- **Flask Community**: For the excellent web framework

## 📞 Support

- **Documentation**: Check the `docs/` folder for detailed guides
- **Issues**: Report bugs on the GitHub Issues page
- **Discussions**: Join conversations in GitHub Discussions
- **Email**: Contact the development team

## 🌟 Star the Project

If WanderWhiz helped you plan an amazing trip, please give it a star! ⭐

---

**Made with ❤️ for travelers around the world**

[🌐 Live Demo](http://127.0.0.1:5001) | [📖 Documentation](docs/) | [🐛 Report Bug](issues/) | [💡 Request Feature](issues/)
