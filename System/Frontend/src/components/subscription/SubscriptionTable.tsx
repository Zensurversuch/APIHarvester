import React, { useEffect, useState } from 'react';
import { Button, Table, Modal, Spinner, Alert } from 'react-bootstrap';
import { useAuth } from '../../contexts/AuthContext';
import { fetchSubscriptions, Subscription, unsubscribe, subscribe } from '../../services/subscription/subscriptionService';
import { useAPI, ApiData } from '../../contexts/ApiDataContext';
import StatusMessage from '../util/StatusMessage';
import { useNavigate } from 'react-router-dom';

const SubscriptionTable: React.FC = () => {
  const { userID } = useAuth();
  const { apiData, loading: apiLoading, error: apiError } = useAPI();
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedApi, setSelectedApi] = useState<ApiData | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [statusType, setStatusType] = useState<'success' | 'failure'>('success');
  const navigate = useNavigate();

  const loadSubscriptions = async () => {
    if (userID) {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchSubscriptions(userID);
        setSubscriptions(data);
      } catch (err) {
        setError('Failed to fetch subscriptions');
      } finally {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    loadSubscriptions();
  }, [userID]);

  // Combine subscriptions with API data
  const combinedData = subscriptions.map((sub) => ({
    subscription: sub,
    api: apiData.find(api => api.availableApiID === sub.availableApiID)
  }));

  const handleApiNameClick = (api: ApiData, e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedApi(api);
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedApi(null);
  };

  const handleRowClick = (subscriptionID: number, apiID: number) => {
    navigate(`/subscriptionData/${subscriptionID}/${apiID}`); // Navigate to the DisplayData page
  };

  const handleSubscribe = async (apiID: number, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      //TODO michi not working
      const interval = 60; 
      await subscribe(userID, apiID, interval);
      setStatusMessage('Subscription successful!');
      setStatusType('success');
      const data = await fetchSubscriptions(userID);
      setSubscriptions(data);
    } catch (error) {
      setStatusMessage('Failed to subscribe.');
      setStatusType('failure');
    }
  };

  const handleUnsubscribe = async (subscriptionID: number, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await unsubscribe(subscriptionID)
      setStatusMessage('Unsubscribing  successful!');
      setStatusType('success');
      loadSubscriptions();
    } catch (error) {
      if (error instanceof Error) {
          setStatusMessage(error.message);
        } else {
          setStatusMessage('An unknown error occurred.');
        }
        setStatusType('failure');
    }
  };

  if (loading || apiLoading) return (
    <div className="text-center mt-5">
      <Spinner animation="border" role="status">
        <span className="visually-hidden">Loading...</span>
      </Spinner>
    </div>
  );

  if (error || apiError) return (
    <div className="text-center mt-5">
      <Alert variant="danger">{error || apiError}</Alert>
    </div>
  );

  return (
    <>
      {statusMessage && (
        <StatusMessage 
          message={statusMessage}
          type={statusType}
          onClose={() => setStatusMessage(null)} // Clear message on close
        />
      )}
      <Table striped bordered hover>
        <thead>
          <tr>
            <th>Subscription ID</th>
            <th>API Name</th>
            <th>API Description</th>
            <th>Interval</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {combinedData.map(({ subscription, api }) => (
            <tr 
              key={subscription.subscriptionID}
              onClick={() => handleRowClick(subscription.subscriptionID, api?.availableApiID || 0)}
              style={{ cursor: 'pointer' }}
            >
              <td>{subscription.subscriptionID}</td>
              <td>
                {api ? (
                  <Button
                    variant="link"
                    onClick={(e) => handleApiNameClick(api, e)}
                  >
                    {api.name}
                  </Button>
                ) : (
                  'Unknown API'
                )}
              </td>
              <td>{api ? api.description : 'No description available'}</td>
              <td>{subscription.interval} seconds</td>
              <td style={{ color: subscription.status === 'ACTIVE' ? 'green' : 'red' }}>
                {subscription.status}
              </td>
              <td>
                {subscription.status === 'ACTIVE' && (
                  <Button
                    variant="danger"
                    onClick={(e) => handleUnsubscribe(subscription.subscriptionID, e)}
                  >
                    Unsubscribe
                  </Button>
                )}
                {subscription.status === 'INACTIVE' && (
                  <Button
                    variant="primary"
                    onClick={(e) => handleSubscribe(subscription.availableApiID, e)}
                  >
                    Subscribe
                  </Button>
                )}
                {subscription.status !== 'ACTIVE' && subscription.status !== 'INACTIVE' && (
                  <Button
                    variant="secondary"
                    disabled
                  >
                    Not Available
                  </Button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </Table>

      <Modal show={showModal} onHide={handleCloseModal}>
        <Modal.Header closeButton>
          <Modal.Title>API Details</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedApi ? (
            <div>
              <h5>{selectedApi.description}</h5>
              <p><strong>Subscription Type:</strong> {selectedApi.subscriptionType}</p>
              <p><strong>URL:</strong> {selectedApi.url}</p>
              <p><strong>Relevant Fields:</strong> {selectedApi.relevantFields.join(', ')}</p>
            </div>
          ) : (
            <p>No API selected</p>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleCloseModal}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default SubscriptionTable;
