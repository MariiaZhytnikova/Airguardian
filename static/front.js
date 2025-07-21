async function fetchViolations() {
	const container = document.getElementById('violations-container');
	container.innerHTML = '<p>Loading violations data...</p>';
  
	try {
		const response = await fetch('http://localhost:8000/frontend-nfz');
		if (!response.ok) {
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
}

function displayViolations(violations) {
	const container = document.getElementById('violations-container');
	container.innerHTML = '';
  
	violations.forEach(violation => {
		const violationElement = document.createElement('div');
		violationElement.className = 'violation-card';
		violationElement.innerHTML = `
			<h3>Violation at (${violation.x}, ${violation.y}, ${violation.z})</h3>
			<p>Time: ${new Date(violation.timestamp).toLocaleString()}</p>
			<p>Owner: ${violation.owner.first_name} ${violation.owner.last_name}</p>
			<p>Contact: ${violation.owner.phone_number}</p>
		`;
		
		container.appendChild(violationElement);
	});
}

// Call this function when your page loads
document.addEventListener('DOMContentLoaded', fetchViolations);