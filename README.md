<h1><strong>NerdRMM — Simple Remote Monitoring and Management Tool</strong></h1>
<p>NerdRMM is a lightweight RMM tool for monitoring system health and managing computer inventory tied to user accounts. It collects system resource data and supports manual inventory input via a simple desktop agent.</p>

<hr>

<h2>⚙️ <strong>Technical Stack</strong></h2>

<h3><strong>Backend & API</strong></h3>
<p>FastAPI handles all reporting and inventory endpoints. PostgreSQL (hosted on AWS RDS) stores system and user inventory data.</p>

<h3><strong>Agent</strong></h3>
<p>A Python-based desktop app (Tkinter) runs on each client, collecting and reporting system metrics.</p>

<hr>

<h2>🚀 <strong>Deployment</strong></h2>
<p>Ansible automates the full infrastructure setup:</p>
<ul>
  <li>Provisions two EC2 instances in separate AWS availability zones</li>
  <li>Sets up an Application Load Balancer (ALB) to distribute traffic across the servers</li>
  <li>Deploys the FastAPI app to both instances</li>
  <li>Pulls source code from GitHub and starts the server in a screen session for persistence</li>
</ul>
