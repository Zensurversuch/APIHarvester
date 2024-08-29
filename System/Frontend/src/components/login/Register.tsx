import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Container, Row, Col, Form, Button } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { register } from '../../services/authentication/registerService';

const Register: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const role = "USER" // Placeholder if the System have multiple Roles
  const [error, setError] = useState<string | null>(null);

  const validatePassword = (password: string) => {
    const minLength = 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

    return (
      password.length >= minLength &&
      hasUpperCase &&
      hasLowerCase &&
      hasNumber &&
      hasSpecialChar
    );
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!validatePassword(password)) {
      setError(t('registerPasswordHelpText'));
      return;
    }
    if (password !== confirmPassword) {
      setError(t('registerPasswordMismatch'));
      return;
    }
    try {
      await register({email, password, lastName, firstName, role});
      navigate('/login', { state: { message: t('userCreatedSuccess') } });
    } catch (error) {
      console.error('Error during registration:', error);
      setError(t('registerError'));
    }
  };

  return (
    <Container className="text-center mt-5">
      <Row className="justify-content-md-center">
        <Col md={6}>
          <h1>{t('register')}</h1>
          <p className="lead mt-3">{t('registerDescription')}</p>

          {error && <div className="alert alert-danger">{error}</div>}

          <Form onSubmit={handleSubmit}>
            <Form.Group controlId="formBasicFirstName">
              <Form.Label>{t('registerFirstName')}</Form.Label>
              <Form.Control
                type="text"
                placeholder={t('registerPlaceholderFirstName')}
                onChange={(e) => setFirstName(e.target.value)}
                required
              />
            </Form.Group>

            <Form.Group controlId="formBasicLastName" className="mt-3">
              <Form.Label>{t('registerLastName')}</Form.Label>
              <Form.Control
                type="text"
                placeholder={t('registerPlaceholderLastName')}
                onChange={(e) => setLastName(e.target.value)}
                required
              />
            </Form.Group>

            <Form.Group controlId="formBasicEmail" className="mt-3">
              <Form.Label>{t('registerEmail')}</Form.Label>
              <Form.Control
                type="email"
                placeholder={t('registerPlaceholderEmail')}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </Form.Group>

            <Form.Group controlId="formBasicPassword" className="mt-3">
              <Form.Label>{t('registerPassword')}</Form.Label>
              <Form.Control
                type="password"
                placeholder={t('registerPlaceholderPassword')}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </Form.Group>

            <Form.Group controlId="formBasicConfirmPassword" className="mt-3">
              <Form.Label>{t('registerConfirmPassword')}</Form.Label>
              <Form.Control
                type="password"
                placeholder={t('registerPlaceholderConfirmPassword')}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
              <Form.Text className="text-muted">
                {t('registerPasswordHelpText')}
              </Form.Text>
            </Form.Group>

            <Button variant="primary" type="submit" className="mt-4 w-100">
              {t('register')}
            </Button>
          </Form>

          <div className="mt-3">
            <small>
              {t('loginRedirectText')} <a href="/login">{t('loginRedirectLink')}</a>
            </small>
          </div>
        </Col>
      </Row>
    </Container>
  );
};

export default Register;
