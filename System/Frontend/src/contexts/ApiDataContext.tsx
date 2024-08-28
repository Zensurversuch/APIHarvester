import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { availableApis } from '../services/availableApis/availalbeApisService';


interface ApiData {
  availableApiID: number;
  description: string;
  relevantFields: string[];
  subscriptionType: string;
  url: string;
}

interface APIContextType {
  apiData: ApiData[]; // Adjusted to match your JSON structure
  loading: boolean;
  error: string | null;
  refreshApiData: () => void;
}

const APIContext = createContext<APIContextType | undefined>(undefined);

export const APIProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [apiData, setApiData] = useState<ApiData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchApiData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await availableApis();
      setApiData(data); // Expecting data in the shape of ApiData[]
    } catch (err) {
      setError('Failed to fetch API data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApiData();
  }, []);

  const refreshApiData = () => {
    fetchApiData();
  };

  return (
    <APIContext.Provider value={{ apiData, loading, error, refreshApiData }}>
      {children}
    </APIContext.Provider>
  );
};

export const useAPI = () => {
  const context = useContext(APIContext);
  if (!context) {
    throw new Error('useAPI must be used within an APIProvider');
  }
  return context;
};