// Replace your current fetchViolations function with this more secure approach:

// Store the secret in a closure for better security
const createSecureAPI = () => {
    // In production, this would come from a secure login process
    const apiKey = localStorage.getItem('api_key') || prompt('Enter API key:');
    
    if (apiKey) {
        localStorage.setItem('api_key', apiKey);
    }
    
    return {
        async fetchViolations() {
            const container = document.getElementById('violations-container');
            container.innerHTML = '<p>Loading violations data...</p>';
            
            try {
                // Use the secured endpoint instead of the dev endpoint
                const response = await fetch('http://localhost:8000/nfz', {
                    headers: {
                        'X-Secret': apiKey
                    }
                });
                
                if (!response.ok) {
                    if (response.status === 401) {
                        // Clear invalid key and retry
                        localStorage.removeItem('api_key');
                        alert('Invalid API key. Please try again.');
                        location.reload();
                        return;
                    }
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                
                const violations = await response.json();
                
                if (violations.length === 0) {
                    container.innerHTML = '<p>No violations found in the last 24 hours.</p>';
                } else {
                    displayViolations(violations);
                }
            } catch (error) {
                container.innerHTML = `<p class="error">Error fetching violations: ${error.message}</p>`;
                console.error('Error fetching violations:', error);
            }
        },
        
        logout() {
            localStorage.removeItem('api_key');
            location.reload();
        }
    };
};

// Create secure API instance
const api = createSecureAPI();

// Update the event listener
document.addEventListener('DOMContentLoaded', () => api.fetchViolations());

// Add logout functionality
function setupLogout() {
    const logoutBtn = document.createElement('button');
    logoutBtn.innerText = 'Logout';
    logoutBtn.onclick = api.logout;
    document.body.appendChild(logoutBtn);
}

document.addEventListener('DOMContentLoaded', setupLogout);

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Create limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Then add rate limiting to your endpoints
@app.get("/nfz")
@limiter.limit("5/minute")  # Adjust as needed
def get_violations(
    x_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    # ... rest of your function