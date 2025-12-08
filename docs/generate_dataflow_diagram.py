# Option A: Generate using Python (Graphviz)
# File: /docs/generate_dataflow_diagram.py

from graphviz import Digraph

def create_dataflow_diagram():
    dot = Digraph(comment='Nourish Beauty ETL Data Flow')
    dot.attr(rankdir='LR', size='10,8')
    
    # Data Sources
    with dot.subgraph(name='cluster_sources') as c:
        c.attr(label='Data Sources', style='filled', color='lightblue')
        c.node('csv_sales', 'SuperMarket\nAnalysis.csv')
        c.node('csv_hr', 'HRDataset\nv14.csv')
        c.node('csv_marketing', 'Marketing\nCampaign.csv')
        c.node('api_instagram', 'Instagram\nGraph API')
    
    # Staging
    with dot.subgraph(name='cluster_staging') as c:
        c.attr(label='Staging Area', style='filled', color='lightyellow')
        c.node('staging_sales', 'staging_sales')
        c.node('staging_hr', 'staging_hr')
        c.node('staging_marketing', 'staging_marketing')
        c.node('staging_social', 'staging_social_media')
    
    # Data Warehouse
    with dot.subgraph(name='cluster_dwh') as c:
        c.attr(label='Data Warehouse (PostgreSQL)', style='filled', color='lightgreen')
        
        # Dimensions
        c.node('dim_produk', 'dim_produk')
        c.node('dim_customer', 'dim_customer')
        c.node('dim_employee', 'dim_employee')
        c.node('dim_cabang', 'dim_cabang')
        c.node('dim_payment', 'dim_payment')
        c.node('dim_tanggal', 'dim_tanggal')
        
        # Facts
        c.node('fact_sales', 'fact_sales')
        c.node('fact_marketing', 'fact_marketing_response')
        c.node('fact_employee', 'fact_employee_performance')
        c.node('fact_user', 'fact_user_interaction')
    
    # Dashboard
    dot.node('dashboard', 'Streamlit\nDashboard BI', shape='box3d', color='purple')
    
    # Edges - Extract
    dot.edge('csv_sales', 'staging_sales', label='Extract')
    dot.edge('csv_hr', 'staging_hr', label='Extract')
    dot.edge('csv_marketing', 'staging_marketing', label='Extract')
    dot.edge('api_instagram', 'staging_social', label='Extract')
    
    # Edges - Transform & Load
    dot.edge('staging_sales', 'dim_produk', label='Transform\n& Load')
    dot.edge('staging_sales', 'dim_cabang', label='Transform\n& Load')
    dot.edge('staging_sales', 'dim_payment', label='Transform\n& Load')
    dot.edge('staging_sales', 'fact_sales', label='Load')
    
    dot.edge('staging_hr', 'dim_employee', label='Transform\n& Load')
    dot.edge('staging_hr', 'fact_employee', label='Load')
    
    dot.edge('staging_marketing', 'dim_customer', label='Transform\n& Load')
    dot.edge('staging_marketing', 'fact_marketing', label='Load')
    
    dot.edge('staging_social', 'fact_user', label='Load')
    
    # Edges - Dashboard
    dot.edge('fact_sales', 'dashboard')
    dot.edge('fact_marketing', 'dashboard')
    dot.edge('fact_employee', 'dashboard')
    dot.edge('fact_user', 'dashboard')
    
    # Render
    dot.render('/docs/Nourish_Beauty_DataFlow_Diagram', format='png', cleanup=True)
    print("✅ Data Flow Diagram generated: /docs/Nourish_Beauty_DataFlow_Diagram.png")

if __name__ == '__main__':
    create_dataflow_diagram()
