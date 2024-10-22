import React, { useState, useEffect } from 'react';
import { Table, Form, Spinner, Alert, Button } from 'react-bootstrap';
import { useAPI, ApiData } from '../../contexts/ApiDataContext';
import { subscriptionData } from '../../services/subscription/subscriptionDataService';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

interface DataPoint {
  _measurement: string;
  _start: string;
  _stop: string;
  _time: string;
  fetchTimestamp: string;
  result: string;
  subscriptionID: number;
  table: number;
  value: string;
}

const DisplayData: React.FC = () => {
  const { getAndCheckToken } = useAuth();
  const { subscriptionID: subscriptionIDString, apiID: apiIDString } = useParams<{ subscriptionID: string; apiID: string }>();
  const subscriptionID = Number(subscriptionIDString);
  const apiID = Number(apiIDString);
  const { apiData, loading: apiLoading, error: apiError } = useAPI();
  const [data, setData] = useState<DataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timespan, setTimespan] = useState<number>(60);
  const [timespanError, setTimespanError] = useState<string | null>(null);

  const navigate = useNavigate();
  // get API data
  const selectedApi = apiData.find((api: ApiData) => api.availableApiID === apiID);
  const relevantFields = new Set(selectedApi?.relevantFields || []);

  // get all relevant fields data from dataObject even if they are encapsulated
  function extractRelevantFields(dataObject: any): Record<string, any> {
    let result: Record<string, any> = {};

    for (const key in dataObject) {
      if (relevantFields.has(key)) {
        result[key] = dataObject[key];
      } else if (typeof dataObject[key] === 'object' && dataObject[key] !== null) {
        const nestedResult = extractRelevantFields(dataObject[key]);
        Object.assign(result, nestedResult);
      }
    }

    return result;
  }

  // fetch subscription Data
  const fetchData = async () => {
    if (!selectedApi) {
        setError('API not found');
        setLoading(false);
        return;
      }
      
    try {
      const response = await subscriptionData(getAndCheckToken(), subscriptionID, timespan);
      setData(response);
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError('An unknown error occurred. Please try again later.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!apiLoading) {
        fetchData();
      }
    }, [selectedApi, timespan, subscriptionID, apiLoading]);

  // check if the selected timespan is in range and set timespan  
  const handleTimespanChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = Number(e.target.value);
    if (value < 1) {
      setTimespanError('Timespan must be at least 1 minute.');
    } else if (value > 518400) {
      setTimespanError('Timespan must not exceed 518,400 minutes (360 days).');
    } else {
      setTimespanError(null);
      setTimespan(value);
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

  // Convert the fetched API data in order to show them in the right format
  const parsedData = data.map(point => {
    try {
      const parsedValue = JSON.parse(point.value);

      // Check if 'current' exists and handle accordingly
      if (parsedValue.current) {
        const valueWithUnits = Object.keys(parsedValue.current).reduce<Record<string, string>>((acc, key) => {
          const unit = parsedValue.current_units?.[key] || ''; 
          acc[key] = `${parsedValue.current[key]}${unit}`; 
          return acc;
        }, {});
  
        return {
          ...point,
          value: valueWithUnits 
        };
      } else {
        const relevantData = extractRelevantFields(parsedValue);
        return {
          ...point,
          value: relevantData
        };
      }
    } catch (error) {
      console.error('Error parsing JSON:', error);
      return {
        ...point,
        value: {} // Handle parsing errors by returning an empty object
      };
    }
  });

  return (
    <div>
      <div className="d-flex justify-content-between mb-3">
        <Button variant="secondary" onClick={() => navigate(-1)}>
          Go Back
        </Button>
        <Button variant="primary" onClick={fetchData}>
          Refresh
        </Button>
      </div>

      <Form.Group controlId="timespanControl">
        <Form.Label>Select Timespan (minutes)</Form.Label>
        <Form.Control
          type="number"
          value={timespan}
          onChange={handleTimespanChange}
        />
        {timespanError && (
            <div className="text-center mb-3">
                <Alert variant="warning">{timespanError}</Alert>
            </div>
        )}
      </Form.Group>

      {data.length === 0 ? (
        <div className="text-center mb-3">
            <Alert variant="info">No data available for the selected timespan. Please adjust the timespan or check back later.</Alert>
        </div>
      ) : (
        <Table striped bordered hover>
          <thead>
            <tr>
              <th>Time</th>
              {selectedApi?.relevantFields.map(field => (
                <th key={field}>{field}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {parsedData.map((point, index) => (
              <tr key={index}>
                <td>{new Date(point._time).toLocaleString()}</td>
                {selectedApi?.relevantFields.map(field => (
                  <td key={field}>{point.value[field] || 'N/A'}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </div>
  );
};

export default DisplayData;
