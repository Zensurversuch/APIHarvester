//import { useAuth } from '../../contexts/AuthContext';
import { POSTGRES_API_BASE_URL } from '../apiConfig'
import { getAuthData } from '../authentication/authService';
 

export const availableApis = async () => {
    const {token} = getAuthData();
    const response = await fetch(POSTGRES_API_BASE_URL + 'availableApis', {
      method: 'GET',
     headers: {
       'Authorization': `Bearer ${token}`,  
       'Content-Type': 'application/json',
     },
    });
  
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
  
    return response.json();
  };