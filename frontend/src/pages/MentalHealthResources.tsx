import React from 'react';
import {
    Box,
    Typography,
    Paper,
    Grid,
    Divider,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Card,
    CardContent,
    useTheme,
} from '@mui/material';
import {
    Favorite as FavoriteIcon,
    SelfImprovement as SelfImprovementIcon,
    Psychology as PsychologyIcon,
    Spa as SpaIcon,
    MedicalServices as MedicalServicesIcon,
    Healing as HealingIcon,
    LocalHospital as LocalHospitalIcon,
    Group as GroupIcon,
} from '@mui/icons-material';

const MentalHealthResources: React.FC = () => {
    const theme = useTheme();

    return (
        <Box sx={{ p: 3, backgroundColor: '#fff0f5' }}>
            <Typography variant="h4" gutterBottom sx={{ color: '#d84f8b', fontWeight: 'bold', fontFamily: '"Playfair Display", serif' }}>
                Women's Mental Health Resources
            </Typography>
            
            <Typography variant="body1" color="text.secondary" paragraph sx={{ fontSize: '1.1rem', lineHeight: 1.6 }}>
                Women face unique mental health challenges influenced by biological factors, societal expectations, and life experiences.
                This page provides information about therapy approaches, self-care practices, and resources specifically designed to support women's mental health.
            </Typography>

            <Paper sx={{ p: 4, mb: 4, borderRadius: 2, boxShadow: '0 4px 12px rgba(216, 79, 139, 0.15)', border: '1px solid #f8bbd0' }}>
                <Typography variant="h5" gutterBottom sx={{ color: '#ad1457', fontFamily: '"Playfair Display", serif' }}>
                    Understanding Women's Mental Health
                </Typography>
                
                <Typography variant="body1" paragraph sx={{ lineHeight: 1.6 }}>
                    Women's mental health is influenced by a complex interplay of biological, psychological, and social factors. Hormonal fluctuations
                    throughout the menstrual cycle, during pregnancy, postpartum, and menopause can significantly impact mood and emotional well-being.
                    Additionally, women often face unique societal pressures, including balancing multiple roles, gender discrimination, and higher rates
                    of certain types of trauma.
                </Typography>
                
                <Typography variant="body1" paragraph sx={{ lineHeight: 1.6 }}>
                    Research shows that women are more likely than men to experience certain mental health conditions, including depression, anxiety,
                    PTSD, and eating disorders. However, women also tend to have stronger social support networks and are often more willing to seek help,
                    which can be protective factors for mental health.
                </Typography>
                
                <Box sx={{ backgroundColor: '#f3e5f5', p: 2, borderRadius: 2, mb: 3 }}>
                    <Typography variant="body1" sx={{ fontStyle: 'italic', color: '#6a1b9a', lineHeight: 1.6 }}>
                        "The expectation that we can be immersed in suffering and loss daily and not be touched by it is as unrealistic as expecting to
                        be able to walk through water without getting wet." — Rachel Naomi Remen, MD
                    </Typography>
                </Box>
            </Paper>

            <Grid container spacing={4}>
                <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 3, height: '100%', borderRadius: 2, boxShadow: '0 4px 12px rgba(216, 79, 139, 0.15)', border: '1px solid #f8bbd0' }}>
                        <Typography variant="h5" gutterBottom sx={{ color: '#ad1457', fontFamily: '"Playfair Display", serif' }}>
                            Effective Therapy Approaches
                        </Typography>
                        
                        <List>
                            <ListItem>
                                <ListItemIcon>
                                    <PsychologyIcon sx={{ color: '#d84f8b' }} />
                                </ListItemIcon>
                                <ListItemText 
                                    primary="Cognitive Behavioral Therapy (CBT)" 
                                    secondary="Helps identify and change negative thought patterns that affect emotions and behaviors. Particularly effective for depression and anxiety disorders common in women."
                                />
                            </ListItem>
                            <Divider variant="inset" component="li" />
                            
                            <ListItem>
                                <ListItemIcon>
                                    <HealingIcon sx={{ color: '#d84f8b' }} />
                                </ListItemIcon>
                                <ListItemText 
                                    primary="Interpersonal Therapy (IPT)" 
                                    secondary="Focuses on improving interpersonal relationships and social functioning. Effective for depression related to relationship issues, role transitions, and grief."
                                />
                            </ListItem>
                            <Divider variant="inset" component="li" />
                            
                            <ListItem>
                                <ListItemIcon>
                                    <SelfImprovementIcon sx={{ color: '#d84f8b' }} />
                                </ListItemIcon>
                                <ListItemText 
                                    primary="Mindfulness-Based Cognitive Therapy" 
                                    secondary="Combines mindfulness practices with cognitive therapy to prevent depression relapse and reduce anxiety. Helps women develop awareness of thoughts without judgment."
                                />
                            </ListItem>
                            <Divider variant="inset" component="li" />
                            
                            <ListItem>
                                <ListItemIcon>
                                    <GroupIcon sx={{ color: '#d84f8b' }} />
                                </ListItemIcon>
                                <ListItemText 
                                    primary="Group Therapy" 
                                    secondary="Provides validation, support, and connection with others experiencing similar challenges. Women-specific groups can address unique issues like motherhood, body image, or trauma recovery."
                                />
                            </ListItem>
                        </List>
                    </Paper>
                </Grid>
                
                <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 3, height: '100%', borderRadius: 2, boxShadow: '0 4px 12px rgba(216, 79, 139, 0.15)', border: '1px solid #f8bbd0' }}>
                        <Typography variant="h5" gutterBottom sx={{ color: '#ad1457', fontFamily: '"Playfair Display", serif' }}>
                            Self-Care Practices for Mental Wellness
                        </Typography>
                        
                        <List>
                            <ListItem>
                                <ListItemIcon>
                                    <SpaIcon sx={{ color: '#d84f8b' }} />
                                </ListItemIcon>
                                <ListItemText 
                                    primary="Mindfulness and Meditation" 
                                    secondary="Regular practice can reduce stress, anxiety, and depression while improving emotional regulation. Even 5-10 minutes daily can make a difference."
                                />
                            </ListItem>
                            <Divider variant="inset" component="li" />
                            
                            <ListItem>
                                <ListItemIcon>
                                    <FavoriteIcon sx={{ color: '#d84f8b' }} />
                                </ListItemIcon>
                                <ListItemText 
                                    primary="Physical Movement" 
                                    secondary="Regular exercise releases endorphins and can significantly reduce symptoms of depression and anxiety. Choose activities you enjoy, whether yoga, dancing, walking, or swimming."
                                />
                            </ListItem>
                            <Divider variant="inset" component="li" />
                            
                            <ListItem>
                                <ListItemIcon>
                                    <MedicalServicesIcon sx={{ color: '#d84f8b' }} />
                                </ListItemIcon>
                                <ListItemText 
                                    primary="Hormone-Aware Self-Care" 
                                    secondary="Track your menstrual cycle and adjust self-care practices accordingly. During premenstrual phases, you may need more rest, gentler exercise, and emotional support."
                                />
                            </ListItem>
                            <Divider variant="inset" component="li" />
                            
                            <ListItem>
                                <ListItemIcon>
                                    <LocalHospitalIcon sx={{ color: '#d84f8b' }} />
                                </ListItemIcon>
                                <ListItemText 
                                    primary="Setting Boundaries" 
                                    secondary="Learning to say no and set healthy boundaries is crucial for women's mental health. Practice identifying your limits and communicating them clearly."
                                />
                            </ListItem>
                        </List>
                    </Paper>
                </Grid>
            </Grid>

            <Box sx={{ mt: 4 }}>
                <Typography variant="h5" gutterBottom sx={{ color: '#ad1457', fontFamily: '"Playfair Display", serif' }}>
                    Common Mental Health Challenges for Women
                </Typography>
                
                <Grid container spacing={3} sx={{ mt: 1 }}>
                    <Grid item xs={12} sm={6} md={4}>
                        <Card sx={{ height: '100%', boxShadow: '0 4px 12px rgba(216, 79, 139, 0.15)', border: '1px solid #f8bbd0' }}>
                            <CardContent>
                                <Typography variant="h6" gutterBottom sx={{ color: '#ad1457' }}>
                                    Depression
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Women are twice as likely as men to experience depression. Hormonal changes, societal pressures, and higher rates of trauma contribute to this disparity. Symptoms may include persistent sadness, loss of interest in activities, fatigue, and changes in sleep or appetite.
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                    
                    <Grid item xs={12} sm={6} md={4}>
                        <Card sx={{ height: '100%', boxShadow: '0 4px 12px rgba(216, 79, 139, 0.15)', border: '1px solid #f8bbd0' }}>
                            <CardContent>
                                <Typography variant="h6" gutterBottom sx={{ color: '#ad1457' }}>
                                    Anxiety Disorders
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Women are more likely to develop anxiety disorders, including generalized anxiety, panic disorder, and specific phobias. Symptoms may include excessive worry, restlessness, difficulty concentrating, and physical symptoms like rapid heartbeat or shortness of breath.
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                    
                    <Grid item xs={12} sm={6} md={4}>
                        <Card sx={{ height: '100%', boxShadow: '0 4px 12px rgba(216, 79, 139, 0.15)', border: '1px solid #f8bbd0' }}>
                            <CardContent>
                                <Typography variant="h6" gutterBottom sx={{ color: '#ad1457' }}>
                                    Trauma-Related Disorders
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Women experience higher rates of certain traumas, including sexual assault and domestic violence, leading to higher rates of PTSD. Symptoms may include flashbacks, nightmares, avoidance behaviors, and hypervigilance.
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                    
                    <Grid item xs={12} sm={6} md={4}>
                        <Card sx={{ height: '100%', boxShadow: '0 4px 12px rgba(216, 79, 139, 0.15)', border: '1px solid #f8bbd0' }}>
                            <CardContent>
                                <Typography variant="h6" gutterBottom sx={{ color: '#ad1457' }}>
                                    Perinatal Mood Disorders
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Up to 20% of women experience depression or anxiety during pregnancy or postpartum. These conditions are influenced by hormonal changes, sleep deprivation, and the significant life transition of becoming a mother.
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                    
                    <Grid item xs={12} sm={6} md={4}>
                        <Card sx={{ height: '100%', boxShadow: '0 4px 12px rgba(216, 79, 139, 0.15)', border: '1px solid #f8bbd0' }}>
                            <CardContent>
                                <Typography variant="h6" gutterBottom sx={{ color: '#ad1457' }}>
                                    Eating Disorders
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Women are more likely to develop eating disorders like anorexia nervosa, bulimia nervosa, and binge eating disorder. These conditions are influenced by societal pressures regarding body image and can have serious physical and psychological consequences.
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                    
                    <Grid item xs={12} sm={6} md={4}>
                        <Card sx={{ height: '100%', boxShadow: '0 4px 12px rgba(216, 79, 139, 0.15)', border: '1px solid #f8bbd0' }}>
                            <CardContent>
                                <Typography variant="h6" gutterBottom sx={{ color: '#ad1457' }}>
                                    Premenstrual Dysphoric Disorder
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    PMDD is a severe form of PMS affecting 3-8% of women. It involves significant mood symptoms like depression, anxiety, irritability, and mood swings that occur during the luteal phase of the menstrual cycle and improve with menstruation.
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            </Box>

            <Paper sx={{ p: 4, mt: 4, borderRadius: 2, boxShadow: '0 4px 12px rgba(216, 79, 139, 0.15)', border: '1px solid #f8bbd0' }}>
                <Typography variant="h5" gutterBottom sx={{ color: '#ad1457', fontFamily: '"Playfair Display", serif' }}>
                    When to Seek Professional Help
                </Typography>
                
                <Typography variant="body1" paragraph sx={{ lineHeight: 1.6 }}>
                    It's important to recognize when self-care isn't enough and professional support is needed. Consider seeking help if you experience:
                </Typography>
                
                <List>
                    <ListItem>
                        <ListItemIcon>
                            <PsychologyIcon sx={{ color: '#d84f8b' }} />
                        </ListItemIcon>
                        <ListItemText primary="Persistent feelings of sadness, anxiety, or emptiness that don't improve with time" />
                    </ListItem>
                    
                    <ListItem>
                        <ListItemIcon>
                            <PsychologyIcon sx={{ color: '#d84f8b' }} />
                        </ListItemIcon>
                        <ListItemText primary="Difficulty functioning in daily life, including work, relationships, or self-care" />
                    </ListItem>
                    
                    <ListItem>
                        <ListItemIcon>
                            <PsychologyIcon sx={{ color: '#d84f8b' }} />
                        </ListItemIcon>
                        <ListItemText primary="Changes in sleep, appetite, or energy that persist for more than two weeks" />
                    </ListItem>
                    
                    <ListItem>
                        <ListItemIcon>
                            <PsychologyIcon sx={{ color: '#d84f8b' }} />
                        </ListItemIcon>
                        <ListItemText primary="Thoughts of harming yourself or others" />
                    </ListItem>
                    
                    <ListItem>
                        <ListItemIcon>
                            <PsychologyIcon sx={{ color: '#d84f8b' }} />
                        </ListItemIcon>
                        <ListItemText primary="Excessive use of alcohol or drugs to cope with emotions" />
                    </ListItem>
                </List>
                
                <Typography variant="body1" paragraph sx={{ lineHeight: 1.6, mt: 2 }}>
                    Remember that seeking help is a sign of strength, not weakness. Mental health professionals can provide the support, 
                    tools, and treatment needed to help you feel better and improve your quality of life.
                </Typography>
                
                <Box sx={{ backgroundColor: '#f3e5f5', p: 2, borderRadius: 2, mt: 2 }}>
                    <Typography variant="body1" sx={{ fontStyle: 'italic', color: '#6a1b9a', lineHeight: 1.6 }}>
                        "Healing takes time, and asking for help is a courageous step." — Mariska Hargitay
                    </Typography>
                </Box>
            </Paper>
        </Box>
    );
};

export default MentalHealthResources;