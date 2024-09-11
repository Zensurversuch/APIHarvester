import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { availableApis } from '../services/availableApis/availableApisService';
import { useAuth } from './AuthContext';


export interface ApiData {
  availableApiID: number;
  description: string;
  name: string;
  relevantFields: string[];
  subscriptionType: string;
  url: string;
}

interface APIContextType {
  apiData: ApiData[]; 
  loading: boolean;
  error: string | null;
  refreshApiData: () => void;
}

const APIContext = createContext<APIContextType | undefined>(undefined);

export const APIProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [apiData, setApiData] = useState<ApiData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const {getAndCheckToken} = useAuth();

  const fetchApiData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await availableApis(getAndCheckToken());
      setApiData(data);
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