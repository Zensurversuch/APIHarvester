import { POSTGRES_API_BASE_URL } from '../apiConfig'

export const login = async (data: { email: string; password: string }) => {

    const response = await fetch(POSTGRES_API_BASE_URL + 'login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
  
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
  
    return response.json();
  };