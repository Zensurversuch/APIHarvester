import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css'; 

import './index.css';
import Footer from './components/footer/Footer';
import Header from './components/header/Header';
import Home from './components/home/Home';
import Login from './components/login/Login';
import { AuthProvider } from './contexts/AuthContext';
import APIList from './components/apis/APIList';

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="App">
          <Header />
          <div className="content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/apis" element={<APIList apiData={[]} />} />
            </Routes>
          </div>
          <Footer />
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;
