import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Container, Row, Col, Form, Button } from 'react-bootstrap';
import { login } from '../../services/authentication/loginService';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const Login: React.FC = () => {
  const { t } = useTranslation();
  const { setAuthData } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      const result = await login({ email, password });

      // Save the result in the AuthContext
      setAuthData(result.access_token, result.role, result.userID);
      //
      navigate('/');

    } catch (error) {
      console.error('Error during login:', error);
      setError('Login failed. Please check your credentials and try again.');
    }
  };

  return (
    <Container className="text-center mt-5">
      <Row className="justify-content-md-center">
        <Col md={6}>
          <h1>{t('loginTitle')}</h1>
          <p className="lead mt-3">{t('loginDescription')}</p>

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
        </Col>
      </Row>
    </Container>
  );
};

export default Login;
