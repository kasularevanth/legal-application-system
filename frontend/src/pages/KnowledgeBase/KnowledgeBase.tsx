import React from 'react';
import { Container, Typography, Box, Paper, TextField, List, ListItem, ListItemText, Divider } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

// Placeholder for knowledge base article type
interface KBArticle {
  id: string;
  title: string;
  summary: string;
  category: string;
}

const mockArticles: KBArticle[] = [
  { id: '1', title: 'Understanding Legal Jargon', summary: 'A quick guide to common legal terms.', category: 'General Law' },
  { id: '2', title: 'Steps to File a Small Claim', summary: 'Learn how to navigate the small claims court process.', category: 'Civil Procedure' },
  { id: '3', title: 'Tenant Rights and Eviction', summary: 'Know your rights as a tenant facing eviction.', category: 'Housing Law' },
];

const KnowledgeBase: React.FC = () => {
  const [searchTerm, setSearchTerm] = React.useState('');
  const [filteredArticles, setFilteredArticles] = React.useState<KBArticle[]>(mockArticles);

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
    if (event.target.value === '') {
      setFilteredArticles(mockArticles);
    } else {
      setFilteredArticles(
        mockArticles.filter(article =>
          article.title.toLowerCase().includes(event.target.value.toLowerCase()) ||
          article.summary.toLowerCase().includes(event.target.value.toLowerCase())
        )
      );
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Knowledge Base
        </Typography>
        <Typography variant="subtitle1" color="textSecondary" paragraph>
          Find helpful articles and answers to common legal questions.
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Search articles..."
            value={searchTerm}
            onChange={handleSearchChange}
            InputProps={{
              startAdornment: <SearchIcon sx={{ mr: 1, color: 'action.active' }} />,
            }}
          />
        </Box>
      </Paper>

      <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
        {searchTerm ? `Search Results for "${searchTerm}"` : "All Articles"}
      </Typography>

      {filteredArticles.length > 0 ? (
        <List component={Paper} elevation={2}>
          {filteredArticles.map((article, index) => (
            <React.Fragment key={article.id}>
              <ListItem alignItems="flex-start" button component="a" href={`/kb/${article.id}`}> {/* Placeholder link */}
                <ListItemText
                  primary={article.title}
                  secondary={
                    <>
                      <Typography
                        sx={{ display: 'inline' }}
                        component="span"
                        variant="body2"
                        color="text.primary"
                      >
                        {article.category}
                      </Typography>
                      {" — "}{article.summary}
                    </>
                  }
                />
              </ListItem>
              {index < filteredArticles.length - 1 && <Divider component="li" />}
            </React.Fragment>
          ))}
        </List>
      ) : (
        <Typography variant="body1" color="textSecondary" align="center">
          No articles found matching your search criteria.
        </Typography>
      )}
    </Container>
  );
};

export default KnowledgeBase;
