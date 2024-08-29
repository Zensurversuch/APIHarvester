import React, { useEffect, useState } from 'react';
import { Button, Table, Modal } from 'react-bootstrap';
import { useAuth } from '../../contexts/AuthContext';
import { fetchSubscriptions, Subscription } from '../../services/subscription/subscriptionService';
import { useAPI, ApiData } from '../../contexts/ApiDataContext';


const SubscriptionTable: React.FC = () => {
  const { userID } = useAuth();
  const { apiData, loading: apiLoading, error: apiError } = useAPI();
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [selectedApi, setSelectedApi] = useState<ApiData | null>(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
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

    loadSubscriptions();
  }, [userID]);

  // Combine subscriptions with API data
  const combinedData = subscriptions.map((sub) => ({
    subscription: sub,
    api: apiData.find(api => api.availableApiID === sub.availableApiID)
  }));

  if (loading) return <p>Loading subscriptions...</p>;
  if (apiLoading) return <p>Loading API data...</p>;
  if (error) return <p>Error: {error}</p>;
  if (apiError) return <p>Error loading API data: {apiError}</p>;

  const handleApiNameClick = (api: ApiData) => {
    setSelectedApi(api);
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedApi(null);
  };

  return (
    <>
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
            <tr key={subscription.subscriptionID}>
              <td>{subscription.subscriptionID}</td>
              <td>
                {api ? (
                  <Button
                    variant="link"
                    onClick={() => handleApiNameClick(api)}
                  >
                    {api.description}
                  </Button>
                ) : (
                  'Unknown API'
                )}
              </td>
              <td>{api ? api.relevantFields.join(', ') : 'No description available'}</td>
              <td>{subscription.interval} days</td>
              <td style={{ color: subscription.status === 'ACTIVE' ? 'green' : 'red' }}>
                {subscription.status}
              </td>
              <td>
                {subscription.status === 'ACTIVE' && (
                  <Button
                    variant="danger"
                    onClick={async () => {
                      try {
                        await fetch(`/api/subscriptions/${subscription.subscriptionID}`, {
                          method: 'DELETE',
                        });
                        setSubscriptions(prev => prev.filter(sub => sub.subscriptionID !== subscription.subscriptionID));
                      } catch (error) {
                        console.error('Failed to remove subscription:', error);
                      }
                    }}
                  >
                    Unsubscribe
                  </Button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </Table>

      {/* Modal to show detailed API information */}
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
