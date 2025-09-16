# Reckon AI ChatBot Frontend

This repository contains both the user-facing frontend and admin frontend for the Reckon AI ChatBot system, built with React, TypeScript, and Material-UI.

## 🏗️ Project Structure

```
frontend/
├── shared/                    # Shared components and design system
│   ├── components/           # Reusable UI components
│   │   ├── ReckonCard.tsx    # Custom card component
│   │   ├── Layout.tsx        # Main layout component
│   │   ├── ChatInterface.tsx # Chat interface component
│   │   └── index.ts         # Component exports
│   ├── hooks/               # Custom React hooks
│   │   └── useResponsive.ts # Responsive utilities
│   ├── theme.ts             # Material-UI theme configuration
│   └── index.ts             # Main exports
├── user/                     # User-facing application
│   ├── src/
│   │   ├── pages/           # Application pages
│   │   │   ├── HomePage.tsx # Landing page
│   │   │   └── ChatPage.tsx # Chat interface page
│   │   └── App.tsx          # Main app component
│   └── package.json         # User app dependencies
└── admin/                    # Admin application
    ├── src/
    │   ├── components/      # Admin-specific components
    │   │   └── AdminLayout.tsx # Admin layout with sidebar
    │   ├── pages/           # Admin pages
    │   │   ├── DashboardPage.tsx     # Admin dashboard
    │   │   ├── DataManagementPage.tsx # Data management
    │   │   ├── AnalyticsPage.tsx     # Analytics & reports
    │   │   └── SettingsPage.tsx      # System settings
    │   └── App.tsx          # Admin app component
    └── package.json         # Admin app dependencies
```

## 🎨 Design System

The project uses a consistent design system based on the Reckon brand colors:

### Colors
- **Primary Blue**: `#2563EB` - Main brand color for buttons, icons, and accents
- **Background**: `#F8FAFC` - Light grayish-blue background
- **Secondary**: `#64748B` - Gray-blue for secondary elements
- **Success**: `#10B981` - Green for success states
- **Error**: `#EF4444` - Red for error states
- **Warning**: `#F59E0B` - Orange for warning states

### Components
- **ReckonCard**: Custom card component with hover effects and consistent styling
- **Layout**: Main layout component with header, navigation, and responsive design
- **ChatInterface**: Complete chat interface with messages, suggestions, and contact options
- **AdminLayout**: Admin-specific layout with sidebar navigation

## 🚀 Getting Started

### Prerequisites
- Node.js (v16 or later)
- npm or yarn

### Installation

1. **Install User App Dependencies**
   ```bash
   cd frontend/user
   npm install
   ```

2. **Install Admin App Dependencies**
   ```bash
   cd frontend/admin
   npm install
   ```

### Running the Applications

#### User Application (Port 3000)
```bash
cd frontend/user
npm start
```
The user application will be available at `http://localhost:3000`

#### Admin Application (Port 3001)
```bash
cd frontend/admin
PORT=3001 npm start
```
The admin application will be available at `http://localhost:3001`

### Building for Production

#### Build User App
```bash
cd frontend/user
npm run build
```

#### Build Admin App
```bash
cd frontend/admin
npm run build
```

## 📱 Features

### User Application
- **Responsive Design**: Optimized for mobile, tablet, and desktop
- **Chat Interface**: Real-time chat with AI support assistant
- **Popular Questions**: Quick access to common queries
- **Solution Cards**: Easy navigation to different support categories
- **Contact Options**: Direct access to phone, email, and demo booking

### Admin Application
- **Dashboard**: Overview of system metrics and recent activities
- **Data Management**:
  - Knowledge base entries management
  - Training data management
  - Bulk import/export operations
- **Analytics**: Performance metrics and query analytics
- **Settings**: System configuration and AI model settings
- **Responsive Sidebar**: Collapsible navigation for mobile devices

## 🎯 Key Features

### Responsive Design
- Mobile-first approach with progressive enhancement
- Breakpoint-specific layouts and components
- Touch-friendly interfaces for mobile devices
- Optimized typography and spacing for different screen sizes

### Accessibility
- ARIA labels and proper semantic HTML
- Keyboard navigation support
- High contrast ratios for text readability
- Screen reader friendly components

### Performance
- Code splitting with React.lazy()
- Optimized Material-UI components
- Efficient state management
- Image optimization and lazy loading

## 🔧 Configuration

### Environment Variables
Create a `.env` file in each app directory:

**User App (.env)**
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_APP_NAME=Reckon AI Support
```

**Admin App (.env)**
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_APP_NAME=Reckon Admin
```

### Theme Customization
The theme can be customized in `shared/theme.ts`:

```typescript
export const colors = {
  primary: {
    main: '#2563EB',    // Change primary color
    light: '#60A5FA',
    dark: '#1D4ED8',
  },
  // ... other colors
};
```

## 🧪 Testing

### Running Tests
```bash
# User app tests
cd frontend/user
npm test

# Admin app tests
cd frontend/admin
npm test
```

### Test Coverage
```bash
npm test -- --coverage
```

## 📦 Dependencies

### Core Dependencies
- **React** - UI library
- **TypeScript** - Type safety
- **Material-UI** - Component library
- **React Router** - Client-side routing
- **Axios** - HTTP client

### Development Dependencies
- **ESLint** - Code linting
- **Prettier** - Code formatting
- **React Testing Library** - Component testing

## 🚀 Deployment

### Docker Deployment
```dockerfile
# User App Dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /var/www/user-app;
        try_files $uri $uri/ /index.html;
    }

    location /admin {
        root /var/www/admin-app;
        try_files $uri $uri/ /index.html;
    }
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Email: support@reckonsales.in
- Phone: +91-522-XXXXXX
- Documentation: [Link to documentation]

---

Built with ❤️ by the Reckon Team