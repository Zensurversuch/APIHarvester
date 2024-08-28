//import { useAuth } from '../../contexts/AuthContext';
import { API_BASE_URL } from '../apiConfig'
 

export const availableApis = async () => {
    //const { token } = useAuth();
    const response = await fetch(API_BASE_URL + 'availableApis', {
      method: 'GET',
    //  headers: {
     //   'Authorization': `Bearer ${token}`,  
     //   'Content-Type': 'application/json',
     // },
    });
  
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
  
    return response.json();
  };