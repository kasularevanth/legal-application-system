import React from 'react';
import {
  Container, Typography, Paper, Box, Button, List, ListItem, ListItemText,
  Divider, Chip, Select, MenuItem, FormControl, InputLabel
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';

// Placeholder for SupportTicket type
interface SupportTicket {
  id: string;
  subject: string;
  status: 'Open' | 'In Progress' | 'Resolved' | 'Closed';
  lastUpdate: string;
  priority: 'Low' | 'Medium' | 'High';
}

const mockTickets: SupportTicket[] = [
  { id: 'TICKET001', subject: 'Issue with document upload', status: 'Open', lastUpdate: '2024-06-07', priority: 'High' },
  { id: 'TICKET002', subject: 'Login problem on mobile', status: 'In Progress', lastUpdate: '2024-06-06', priority: 'Medium' },
  { id: 'TICKET003', subject: 'Feature request: Dark mode', status: 'Resolved', lastUpdate: '2024-06-05', priority: 'Low' },
];

const SupportTickets: React.FC = () => {
  const [tickets, setTickets] = React.useState<SupportTicket[]>(mockTickets);
  const [filterStatus, setFilterStatus] = React.useState<string>('All');
  const [filterPriority, setFilterPriority] = React.useState<string>('All');

  const handleCreateTicket = () => {
    // Logic to navigate to a new ticket creation page or open a modal
    console.log('Navigate to create new ticket');
  };

  const getStatusColor = (status: SupportTicket['status']) => {
    if (status === 'Open') return 'error';
    if (status === 'In Progress') return 'warning';
    if (status === 'Resolved') return 'success';
    return 'default';
  };
  
  const filteredTickets = tickets.filter(ticket => 
    (filterStatus === 'All' || ticket.status === filterStatus) &&
    (filterPriority === 'All' || ticket.priority === filterPriority)
  );

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" gutterBottom>
            Support Tickets
          </Typography>
          <Button variant="contained" startIcon={<AddIcon />} onClick={handleCreateTicket}>
            Create New Ticket
          </Button>
        </Box>

        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <FormControl sx={{ minWidth: 150 }}>
            <InputLabel>Status</InputLabel>
            <Select value={filterStatus} label="Status" onChange={(e) => setFilterStatus(e.target.value)}>
              <MenuItem value="All">All Statuses</MenuItem>
              <MenuItem value="Open">Open</MenuItem>
              <MenuItem value="In Progress">In Progress</MenuItem>
              <MenuItem value="Resolved">Resolved</MenuItem>
              <MenuItem value="Closed">Closed</MenuItem>
            </Select>
          </FormControl>
          <FormControl sx={{ minWidth: 150 }}>
            <InputLabel>Priority</InputLabel>
            <Select value={filterPriority} label="Priority" onChange={(e) => setFilterPriority(e.target.value)}>
              <MenuItem value="All">All Priorities</MenuItem>
              <MenuItem value="Low">Low</MenuItem>
              <MenuItem value="Medium">Medium</MenuItem>
              <MenuItem value="High">High</MenuItem>
            </Select>
          </FormControl>
        </Box>

        {filteredTickets.length > 0 ? (
          <List>
            {filteredTickets.map((ticket, index) => (
              <React.Fragment key={ticket.id}>
                <ListItem
                  button 
                  onClick={() => console.log(`View ticket ${ticket.id}`)} // Placeholder for navigation
                  secondaryAction={
                    <Chip label={ticket.priority} size="small" color={ticket.priority === 'High' ? 'error' : ticket.priority === 'Medium' ? 'warning' : 'default'} />
                  }
                >
                  <ListItemText
                    primary={ticket.subject}
                    secondary={`ID: ${ticket.id} - Last Update: ${ticket.lastUpdate}`}
                  />
                  <Chip label={ticket.status} size="small" color={getStatusColor(ticket.status)} sx={{ml: 2}} />
                </ListItem>
                {index < filteredTickets.length - 1 && <Divider />}
              </React.Fragment>
            ))}
          </List>
        ) : (
          <Typography variant="body1" color="textSecondary" align="center" sx={{p:3}}>
            No support tickets match your current filters.
          </Typography>
        )}
      </Paper>
    </Container>
  );
};

export default SupportTickets;
