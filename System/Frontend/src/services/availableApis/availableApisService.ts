//import { useAuth } from '../../contexts/AuthContext';
import { useAuth } from '../../contexts/AuthContext';
import { POSTGRES_API_BASE_URL } from '../apiConfig' 

export const availableApis = async () => {
    const {getAndCheckToken} = useAuth();
    const response = await fetch(POSTGRES_API_BASE_URL + 'availableApis', {
      method: 'GET',
     headers: {
       'Authorization': `Bearer ${getAndCheckToken}`,  
       'Content-Type': 'application/json',
     },
    });
  
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
  
    return response.json();
  };