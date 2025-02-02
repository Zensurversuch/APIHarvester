import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Container, Row, Col, Form, Button } from 'react-bootstrap';
import { login } from '../../services/authentication/loginService';
import { useAuth } from '../../contexts/AuthContext';
import { Link, useLocation, useNavigate } from 'react-router-dom';


const Login: React.FC = () => {
  const { t } = useTranslation();
  const location = useLocation();
  const { setAuthData } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

// returns feedback to the user if the register site or the jwt check send a message
  useEffect(() => {
    if (location.state && location.state.message) {
      setMessage(location.state.message);
      window.history.replaceState({}, document.title);
    }
  }, [location.state]);

  // navigate user to home menu if the login was successful
  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      const result = await login({ email, password });

      // Save the result in the AuthContext
      setAuthData(result.access_token, result.role, result.userID);
      navigate('/');

    } catch {
      setError('Login failed. Please check your credentials and try again.');
    }
  };

  return (
    <Container className="text-center mt-5">
      <Row className="justify-content-md-center">
        <Col md={6}>
          <h1>{t('loginTitle')}</h1>
          <p className="lead mt-3">{t('loginDescription')}</p>

          {message && <div className="alert alert-success">{message}</div>}
          {error && <div className="alert alert-danger">{error}</div>}

          <Form onSubmit={handleSubmit}>
            <Form.Group controlId="formBasicEmail">
              <Form.Label>{t('loginEmail')}</Form.Label>
              <Form.Control
                type="email"
                placeholder={t('loginPlaceholderEmail')}    
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </Form.Group>

            <Form.Group controlId="formBasicPassword" className="mt-3">
              <Form.Label>{t('loginPassword')}</Form.Label>
              <Form.Control
                type="password"
                placeholder={t('loginPlaceholderPassword')}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </Form.Group>

            <Button variant="primary" type="submit" className="mt-4 w-100">
              {t('login')}
            </Button>
          </Form>

          <div className="mt-3">
            <small>
              {t('noAccount')} <Link to="/register">{t('registerHere')}</Link>
            </small>
          </div>
        </Col>
      </Row>
    </Container>
  );
};

export default Login;
