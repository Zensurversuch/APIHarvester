import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css'; 

import './index.css';
import Footer from './components/footer/Footer';
import Header from './components/header/Header';
import Home from './components/home/Home';
import Login from './components/login/Login';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/route/ProtectedRoute';
import Register from './components/login/Register';
import { APIProvider } from './contexts/ApiDataContext';
import SubscriptionTable from './components/subscription/SubscriptionTable';
import ApiList from './components/apis/APIList';

function App() {
  return (
    <Router>
      <AuthProvider>
        <APIProvider>
            <div className="App">
              <Header />
              <div className="content">
                <Routes>
                  <Route path="/" element={<Home />} />
                  <Route path="/login" element={<Login />} />
                  <Route path="/register" element={<Register />} />
                  <Route
                    path="/apis" 
                    element={
                      <ProtectedRoute>
                        <ApiList />
                      </ProtectedRoute>
                    }
                  /> 
                  <Route
                    path="/subscriptions" 
                    element={
                      <ProtectedRoute>
                        <SubscriptionTable />
                      </ProtectedRoute>
                    }
                  /> 
                </Routes>
              </div>
              <Footer />
            </div>
        </APIProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;
