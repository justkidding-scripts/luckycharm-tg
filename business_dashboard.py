#!/usr/bin/env python3
"""
Premium Business Dashboard & Sales Management
=============================================
Comprehensive business intelligence and sales management for premium services.
Real-time revenue tracking, client management, and automated sales processes.

Author: Business Intelligence Suite
Version: 1.0.0
"""

import dash
from dash import dcc, html, Input, Output, callback, dash_table
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
import json
from typing import Dict, List
from premium_services import PremiumServicesManager, PremiumMarketingTools

class BusinessDashboard:
    """Comprehensive business dashboard for premium services"""
    
    def __init__(self, services_manager: PremiumServicesManager):
        self.services = services_manager
        self.app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
        self.setup_layout()
        self.setup_callbacks()
        
    def setup_layout(self):
        """Setup dashboard layout"""
        self.app.layout = html.Div([
            html.Div([
                html.H1("💰 Premium Services Business Dashboard", 
                       style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
                
                # KPI Cards
                html.Div([
                    html.Div([
                        html.H3("Monthly Revenue", style={'margin': 0}),
                        html.H2(id="monthly-revenue", style={'color': '#27ae60', 'margin': 0})
                    ], className='four columns', style={'textAlign': 'center', 'backgroundColor': '#ecf0f1', 
                                                       'padding': '20px', 'margin': '10px', 'borderRadius': '10px'}),
                    
                    html.Div([
                        html.H3("Active Clients", style={'margin': 0}),
                        html.H2(id="active-clients", style={'color': '#3498db', 'margin': 0})
                    ], className='four columns', style={'textAlign': 'center', 'backgroundColor': '#ecf0f1', 
                                                       'padding': '20px', 'margin': '10px', 'borderRadius': '10px'}),
                    
                    html.Div([
                        html.H3("Growth Services", style={'margin': 0}),
                        html.H2(id="growth-services", style={'color': '#e74c3c', 'margin': 0})
                    ], className='four columns', style={'textAlign': 'center', 'backgroundColor': '#ecf0f1', 
                                                       'padding': '20px', 'margin': '10px', 'borderRadius': '10px'}),
                ], className='row'),
                
                # Charts Section
                html.Div([
                    html.Div([
                        dcc.Graph(id="revenue-breakdown")
                    ], className='six columns'),
                    
                    html.Div([
                        dcc.Graph(id="service-distribution")  
                    ], className='six columns'),
                ], className='row'),
                
                html.Div([
                    html.Div([
                        dcc.Graph(id="growth-trends")
                    ], className='six columns'),
                    
                    html.Div([
                        dcc.Graph(id="client-satisfaction")
                    ], className='six columns'),
                ], className='row'),
                
                # Client Management Section
                html.Div([
                    html.H2("🎯 Client Management & Sales Pipeline", 
                           style={'textAlign': 'center', 'marginTop': 40}),
                    
                    # Sales Pipeline
                    html.Div([
                        html.H3("Sales Pipeline", style={'marginBottom': 20}),
                        dash_table.DataTable(
                            id='sales-pipeline',
                            columns=[
                                {'name': 'Lead', 'id': 'lead'},
                                {'name': 'Service', 'id': 'service'},
                                {'name': 'Tier', 'id': 'tier'},
                                {'name': 'Value (DKK)', 'id': 'value'},
                                {'name': 'Stage', 'id': 'stage'},
                                {'name': 'Probability', 'id': 'probability'},
                            ],
                            style_cell={'textAlign': 'left', 'padding': '10px'},
                            style_header={'backgroundColor': '#3498db', 'color': 'white'},
                            style_data_conditional=[
                                {
                                    'if': {'filter_query': '{stage} = Closed Won'},
                                    'backgroundColor': '#d5f4e6',
                                },
                                {
                                    'if': {'filter_query': '{stage} = Hot Lead'},
                                    'backgroundColor': '#ffeaa7',
                                }
                            ]
                        )
                    ], style={'marginTop': 30}),
                    
                    # Active Subscriptions
                    html.Div([
                        html.H3("Active Premium Subscriptions", style={'marginTop': 30, 'marginBottom': 20}),
                        dash_table.DataTable(
                            id='active-subscriptions',
                            columns=[
                                {'name': 'Client ID', 'id': 'user_id'},
                                {'name': 'Service', 'id': 'service_category'},
                                {'name': 'Tier', 'id': 'subscription_type'},
                                {'name': 'Monthly (DKK)', 'id': 'monthly_price'},
                                {'name': 'Start Date', 'id': 'start_date'},
                                {'name': 'Renewal', 'id': 'end_date'},
                                {'name': 'Status', 'id': 'status'},
                            ],
                            style_cell={'textAlign': 'left', 'padding': '10px'},
                            style_header={'backgroundColor': '#2c3e50', 'color': 'white'},
                        )
                    ])
                ]),
                
                # Admin Pampering Special Section
                html.Div([
                    html.H2("👑 Premium Admin Pampering Services", 
                           style={'textAlign': 'center', 'marginTop': 50, 'color': '#8e44ad'}),
                    
                    html.Div([
                        # Silver Tier
                        html.Div([
                            html.H3("🥈 Silver Admin", style={'color': '#95a5a6'}),
                            html.P("499 DKK/måned", style={'fontSize': 20, 'fontWeight': 'bold'}),
                            html.Ul([
                                html.Li("Priority support queue"),
                                html.Li("Basic automation scripts"),
                                html.Li("Monthly strategy review"),
                                html.Li("Community access"),
                            ]),
                            html.Button("Upgrade Admin", className='button-primary')
                        ], className='four columns', style={'backgroundColor': '#f8f9fa', 'padding': '20px', 
                                                           'margin': '10px', 'borderRadius': '10px', 'border': '2px solid #95a5a6'}),
                        
                        # Gold Tier  
                        html.Div([
                            html.H3("🥇 Gold Admin", style={'color': '#f39c12'}),
                            html.P("999 DKK/måned", style={'fontSize': 20, 'fontWeight': 'bold'}),
                            html.Ul([
                                html.Li("Dedicated support agent: Sarah K."),
                                html.Li("Advanced automation suite"),
                                html.Li("Weekly strategy calls"),
                                html.Li("VIP community access"),
                                html.Li("Custom feature requests"),
                                html.Li("Growth optimization consulting"),
                            ]),
                            html.Button("Pamper This Admin", className='button-primary')
                        ], className='four columns', style={'backgroundColor': '#fef9e7', 'padding': '20px', 
                                                           'margin': '10px', 'borderRadius': '10px', 'border': '2px solid #f39c12'}),
                        
                        # Platinum Tier
                        html.Div([
                            html.H3("💎 Platinum Admin", style={'color': '#8e44ad'}),
                            html.P("1,999 DKK/måned", style={'fontSize': 20, 'fontWeight': 'bold'}),
                            html.Ul([
                                html.Li("Personal account manager: Michael R."),
                                html.Li("Daily check-ins available"),
                                html.Li("Custom feature development"),
                                html.Li("Direct developer access"),
                                html.Li("Revenue optimization sessions"),
                                html.Li("Exclusive beta features"),
                                html.Li("Luxury welcome package"),
                                html.Li("Quarterly business reviews"),
                            ]),
                            html.Button("Ultimate VIP Treatment", className='button-primary')
                        ], className='four columns', style={'backgroundColor': '#f4f1f8', 'padding': '20px', 
                                                           'margin': '10px', 'borderRadius': '10px', 'border': '2px solid #8e44ad'}),
                    ], className='row'),
                ]),
                
                # Revenue Projections
                html.Div([
                    html.H2("📈 Revenue Projections & Business Intelligence", 
                           style={'textAlign': 'center', 'marginTop': 50}),
                    
                    html.Div([
                        html.Div([
                            dcc.Graph(id="revenue-projection")
                        ], className='twelve columns'),
                    ], className='row'),
                ]),
                
                # Auto-refresh
                dcc.Interval(
                    id='interval-component',
                    interval=30*1000,  # Update every 30 seconds
                    n_intervals=0
                ),
                
            ], style={'padding': '20px'})
        ])
    
    def setup_callbacks(self):
        """Setup dashboard callbacks for interactivity"""
        
        @self.app.callback(
            [Output('monthly-revenue', 'children'),
             Output('active-clients', 'children'),
             Output('growth-services', 'children')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_kpis(n):
            stats = self.services.get_premium_client_stats()
            return (
                f"{stats['monthly_revenue_dkk']:,.0f} DKK",
                f"{stats['total_active_clients']:,}",
                f"{stats['active_growth_services']:,}"
            )
        
        @self.app.callback(
            [Output('revenue-breakdown', 'figure'),
             Output('service-distribution', 'figure'),
             Output('growth-trends', 'figure'),
             Output('client-satisfaction', 'figure'),
             Output('revenue-projection', 'figure')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_charts(n):
            # Get data
            conn = sqlite3.connect(self.services.db_path)
            
            # Revenue breakdown by service
            revenue_data = pd.read_sql_query("""
                SELECT service_category, SUM(monthly_price) as revenue
                FROM subscriptions 
                WHERE is_active = 1
                GROUP BY service_category
            """, conn)
            
            fig1 = px.pie(revenue_data, values='revenue', names='service_category',
                         title="Revenue by Service Type")
            fig1.update_layout(height=400)
            
            # Service distribution
            tier_data = pd.read_sql_query("""
                SELECT subscription_type, COUNT(*) as count
                FROM subscriptions 
                WHERE is_active = 1
                GROUP BY subscription_type
            """, conn)
            
            fig2 = px.bar(tier_data, x='subscription_type', y='count',
                         title="Subscriptions by Tier")
            fig2.update_layout(height=400)
            
            # Growth trends (simulated)
            dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
            growth_data = pd.DataFrame({
                'date': dates,
                'revenue': np.cumsum(np.random.normal(1000, 200, len(dates))) + 10000
            })
            
            fig3 = px.line(growth_data, x='date', y='revenue',
                          title="30-Day Revenue Growth")
            fig3.update_layout(height=400)
            
            # Client satisfaction (simulated)
            satisfaction_data = pd.DataFrame({
                'service': ['Data Analytics', 'Channel Growth', 'Admin Pampering'],
                'satisfaction': [4.8, 4.6, 4.9],
                'clients': [45, 23, 12]
            })
            
            fig4 = px.scatter(satisfaction_data, x='clients', y='satisfaction', 
                             size='clients', color='service',
                             title="Client Satisfaction by Service")
            fig4.update_layout(height=400, yaxis_range=[4.0, 5.0])
            
            # Revenue projection
            future_dates = pd.date_range(start=datetime.now(), end=datetime.now() + timedelta(days=365), freq='M')
            projection_data = pd.DataFrame({
                'month': future_dates,
                'projected_revenue': np.cumsum(np.random.normal(50000, 10000, len(future_dates))) + 100000
            })
            
            fig5 = px.line(projection_data, x='month', y='projected_revenue',
                          title="12-Month Revenue Projection")
            fig5.update_layout(height=400)
            
            conn.close()
            
            return fig1, fig2, fig3, fig4, fig5
        
        @self.app.callback(
            [Output('sales-pipeline', 'data'),
             Output('active-subscriptions', 'data')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_tables(n):
            # Sales pipeline data (simulated)
            pipeline_data = [
                {'lead': 'Lars K. (@cryptodk)', 'service': 'Data Analytics', 'tier': 'Premium', 'value': 799, 'stage': 'Hot Lead', 'probability': '85%'},
                {'lead': 'Anna M. (@nordicshop)', 'service': 'Channel Growth', 'tier': 'Enterprise', 'value': 2999, 'stage': 'Demo Scheduled', 'probability': '60%'},
                {'lead': 'Erik P. (@tradingpro)', 'service': 'Admin Pampering', 'tier': 'Platinum', 'value': 1999, 'stage': 'Proposal Sent', 'probability': '70%'},
                {'lead': 'Mads T. (@techcommunity)', 'service': 'Data Analytics', 'tier': 'Enterprise', 'value': 1999, 'stage': 'Closed Won', 'probability': '100%'},
                {'lead': 'Sofia H. (@lifestyledk)', 'service': 'Channel Growth', 'tier': 'Professional', 'value': 1299, 'stage': 'Negotiating', 'probability': '50%'},
            ]
            
            # Active subscriptions
            conn = sqlite3.connect(self.services.db_path)
            subs_data = pd.read_sql_query("""
                SELECT user_id, service_category, subscription_type, monthly_price,
                       start_date, end_date,
                       CASE WHEN is_active = 1 THEN 'Active' ELSE 'Expired' END as status
                FROM subscriptions
                ORDER BY start_date DESC
            """, conn)
            conn.close()
            
            return pipeline_data, subs_data.to_dict('records')

    def run(self, host='127.0.0.1', port=8050, debug=True):
        """Run the dashboard server"""
        print(f"🚀 Starting Premium Services Dashboard at http://{host}:{port}")
        print("💰 Monitor your revenue, clients, and growth in real-time!")
        self.app.run_server(host=host, port=port, debug=debug)

class AutomatedSalesManager:
    """Automated sales and client management system"""
    
    def __init__(self, services_manager: PremiumServicesManager):
        self.services = services_manager
        self.marketing = PremiumMarketingTools()
        
    def identify_potential_clients(self, channel_data: Dict) -> List[Dict]:
        """Identify potential premium service clients from channel data"""
        potential_clients = []
        
        # Analyze channel data for upgrade opportunities
        if channel_data.get('member_count', 0) > 1000:
            potential_clients.append({
                'channel': channel_data['channel_name'],
                'admin': channel_data.get('admin_username', 'Unknown'),
                'members': channel_data['member_count'],
                'engagement': channel_data.get('engagement_rate', 0.05),
                'recommended_service': 'data_analytics',
                'revenue_potential': channel_data['member_count'] * 15,  # DKK per member
                'probability': min(90, channel_data.get('engagement_rate', 0.05) * 1000 + 40)
            })
        
        if channel_data.get('growth_rate', 0) < 0.02:  # Slow growth
            potential_clients.append({
                'channel': channel_data['channel_name'],
                'admin': channel_data.get('admin_username', 'Unknown'),
                'members': channel_data['member_count'],
                'growth_issue': 'Slow organic growth',
                'recommended_service': 'channel_growth',
                'revenue_potential': 5000,  # Potential monthly revenue increase
                'probability': 65
            })
        
        return potential_clients
    
    def generate_automated_outreach(self, client_data: Dict) -> Dict:
        """Generate personalized outreach messages"""
        service_type = client_data['recommended_service']
        
        pitch = self.marketing.generate_sales_pitch(service_type, {
            'name': client_data['admin'],
            'channel_name': client_data['channel'],
            'members': client_data['members']
        })
        
        return {
            'recipient': client_data['admin'],
            'subject': f"Unlock {client_data['revenue_potential']:,.0f} DKK Revenue in Your {client_data['channel']}",
            'message': pitch,
            'follow_up_days': [3, 7, 14],
            'service_type': service_type,
            'estimated_value': client_data['revenue_potential']
        }
    
    def track_conversion_funnel(self) -> Dict:
        """Track the sales conversion funnel"""
        return {
            'leads_generated': 156,
            'demos_scheduled': 23,
            'proposals_sent': 18,
            'negotiations': 12,
            'closed_won': 8,
            'closed_lost': 4,
            'conversion_rate': 5.1,  # leads to customers
            'avg_deal_size': 1299,
            'sales_cycle_days': 21
        }

def create_comprehensive_business_suite():
    """Create and launch the complete business suite"""
    
    # Initialize services manager
    services = PremiumServicesManager()
    
    # Create sample data for demonstration
    print("🔧 Setting up demo data...")
    
    # Demo subscriptions
    import asyncio
    async def setup_demo():
        await services.create_subscription("lars_k", "data_analytics", "premium")
        await services.create_subscription("anna_m", "channel_growth", "professional")
        await services.create_subscription("erik_p", "admin_pampering", "platinum")
        await services.create_subscription("mads_t", "data_analytics", "enterprise")
        await services.create_subscription("sofia_h", "channel_growth", "starter")
    
    asyncio.run(setup_demo())
    
    # Launch dashboard
    dashboard = BusinessDashboard(services)
    
    print("""
    🎯 PREMIUM SERVICES SUITE READY!
    
    💰 Revenue Streams Active:
    ✅ Data Analytics: 299-1999 DKK/month
    ✅ Channel Growth: 599-2999 DKK/month  
    ✅ Admin Pampering: 499-1999 DKK/month
    
    📊 Dashboard Features:
    • Real-time revenue tracking
    • Client management system
    • Sales pipeline monitoring
    • Growth projections
    • Automated client outreach
    
    🚀 Starting dashboard server...
    """)
    
    return dashboard

if __name__ == "__main__":
    dashboard = create_comprehensive_business_suite()
    dashboard.run(host='0.0.0.0', port=8050)  # Accessible from network