"""
Extract Instagram Data via Graph API
Author: Raudatul Sholehah - 2310817220002

INSTAGRAM GRAPH API DOCUMENTATION:
- Main: https://developers.facebook.com/docs/instagram-api/
- Getting Started: https://developers.facebook.com/docs/instagram-api/getting-started
- Insights: https://developers.facebook.com/docs/instagram-api/reference/ig-user/insights

CARA MENDAPATKAN ACCESS TOKEN:
1. Buat Facebook App: https://developers.facebook.com/apps/
2. Add Instagram Graph API
3. Connect Instagram Business Account
4. Generate Access Token dari Graph API Explorer
5. Copy token dan paste ke config/etl_config.py
"""

import requests
import pandas as pd
from datetime import datetime
import logging
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.etl_config import INSTAGRAM_CONFIG, PATHS
from config.database_config import get_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstagramAPIExtractor:
    """
    Instagram Graph API Extractor Class
    
    API Endpoints yang digunakan:
    1. Get User Media: /{user-id}/media
    2. Get Media Details: /{media-id}
    3. Get Media Insights: /{media-id}/insights
    """
    
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://graph.instagram.com/v21.0/"
        self.session = requests.Session()
        
    def get_user_id(self):
        """
        Get Instagram User ID
        Endpoint: /me
        """
        try:
            url = f"{self.base_url}me"
            params = {
                'fields': 'id,username,account_type',
                'access_token': self.access_token
            }
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Connected to Instagram User: {data.get('username')}")
                logger.info(f"   Account Type: {data.get('account_type')}")
                return data.get('id')
            else:
                logger.error(f"❌ API Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting user ID: {e}")
            return None
    
    def get_user_media(self, user_id, limit=50):
        """
        Get User's Media Posts
        Endpoint: /{user-id}/media
        
        Real API Example:
        https://graph.instagram.com/v21.0/{user-id}/media?fields=id,caption,media_type,media_url,timestamp,like_count,comments_count,permalink&access_token={token}
        """
        try:
            url = f"{self.base_url}{user_id}/media"
            params = {
                'fields': 'id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,username',
                'limit': limit,
                'access_token': self.access_token
            }
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data and len(data['data']) > 0:
                    logger.info(f"✅ Retrieved {len(data['data'])} posts")
                    return data['data']
                else:
                    logger.warning("⚠️  No media found")
                    return []
            else:
                logger.error(f"❌ API Error {response.status_code}: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Error getting media: {e}")
            return []
    
    def get_media_insights(self, media_id):
        """
        Get Media Insights (Engagement Metrics)
        Endpoint: /{media-id}/insights
        
        Available Metrics:
        - engagement: Total interactions
        - impressions: Total views
        - reach: Unique accounts reached
        - saved: Total saves
        
        Real API Example:
        https://graph.instagram.com/v21.0/{media-id}/insights?metric=engagement,impressions,reach,saved&access_token={token}
        """
        try:
            url = f"{self.base_url}{media_id}/insights"
            params = {
                'metric': 'engagement,impressions,reach,saved',
                'access_token': self.access_token
            }
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse insights data
                insights = {}
                if 'data' in data:
                    for metric in data['data']:
                        insights[metric['name']] = metric['values'][0]['value']
                
                return insights
            else:
                # Insights might not be available for all media types
                logger.warning(f"⚠️  Insights not available for media {media_id}")
                return {}
                
        except Exception as e:
            logger.warning(f"⚠️  Could not get insights for {media_id}: {e}")
            return {}
    
    def get_media_details(self, media_id):
        """
        Get detailed media information
        Endpoint: /{media-id}
        
        Real API Example:
        https://graph.instagram.com/v21.0/{media-id}?fields=id,caption,media_type,like_count,comments_count,timestamp&access_token={token}
        """
        try:
            url = f"{self.base_url}{media_id}"
            params = {
                'fields': 'id,caption,media_type,like_count,comments_count,timestamp',
                'access_token': self.access_token
            }
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {}
                
        except Exception as e:
            logger.warning(f"⚠️  Could not get details for {media_id}: {e}")
            return {}

def extract_instagram_posts():
    """
    Main function to extract Instagram data
    """
    try:
        logger.info("🔄 Starting Instagram data extraction...")
        
        access_token = INSTAGRAM_CONFIG['access_token']
        
        # Check if token is configured
        if access_token == 'YOUR_INSTAGRAM_ACCESS_TOKEN':
            logger.warning("=" * 70)
            logger.warning("⚠️  INSTAGRAM ACCESS TOKEN NOT CONFIGURED!")
            logger.warning("=" * 70)
            logger.warning("Untuk mendapatkan Instagram Access Token:")
            logger.warning("")
            logger.warning("STEP 1: Buka Facebook Developers")
            logger.warning("   Link: https://developers.facebook.com/apps/")
            logger.warning("")
            logger.warning("STEP 2: Create New App")
            logger.warning("   - Pilih 'Business' type")
            logger.warning("   - Add Instagram Graph API product")
            logger.warning("")
            logger.warning("STEP 3: Connect Instagram Business Account")
            logger.warning("   - Settings → Basic → Instagram Graph API")
            logger.warning("   - Connect your Instagram Business/Creator account")
            logger.warning("")
            logger.warning("STEP 4: Generate Access Token")
            logger.warning("   Link: https://developers.facebook.com/tools/explorer/")
            logger.warning("   - Select your app")
            logger.warning("   - Add permissions: instagram_basic, instagram_manage_insights")
            logger.warning("   - Generate Access Token")
            logger.warning("")
            logger.warning("STEP 5: Copy token to config/etl_config.py")
            logger.warning("   INSTAGRAM_CONFIG['access_token'] = 'YOUR_TOKEN_HERE'")
            logger.warning("=" * 70)
            logger.warning("")
            logger.warning("📝 Generating SAMPLE DATA untuk testing...")
            
            # Generate sample Instagram data for testing
            return generate_sample_instagram_data()
        
        # Initialize API extractor
        extractor = InstagramAPIExtractor(access_token)
        
        # Get user ID
        user_id = extractor.get_user_id()
        if not user_id:
            logger.error("❌ Failed to get user ID. Check your access token.")
            return None
        
        # Get user's media posts
        media_list = extractor.get_user_media(user_id, limit=50)
        
        if not media_list:
            logger.warning("⚠️  No media posts found")
            return None
        
        # Process each media post
        posts_data = []
        
        for media in media_list:
            media_id = media.get('id')
            
            # Get detailed metrics
            details = extractor.get_media_details(media_id)
            insights = extractor.get_media_insights(media_id)
            
            # Combine data
            post_data = {
                'post_id': media_id,
                'caption': media.get('caption', ''),
                'media_type': media.get('media_type', ''),
                'media_url': media.get('media_url', ''),
                'permalink': media.get('permalink', ''),
                'post_timestamp': media.get('timestamp', ''),
                'like_count': details.get('like_count', 0),
                'comments_count': details.get('comments_count', 0),
                'reach': insights.get('reach', 0),
                'impressions': insights.get('impressions', 0),
                'engagement': insights.get('engagement', 0),
                'saved': insights.get('saved', 0),
                'load_timestamp': datetime.now()
            }
            
            # Calculate engagement rate
            if post_data['reach'] > 0:
                post_data['engagement_rate'] = round(
                    (post_data['engagement'] / post_data['reach']) * 100, 2
                )
            else:
                post_data['engagement_rate'] = 0.0
            
            posts_data.append(post_data)
        
        # Convert to DataFrame
        df = pd.DataFrame(posts_data)
        
        # Save to external folder
        output_file = os.path.join(
            PATHS['external'], 
            f"instagram_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        df.to_csv(output_file, index=False, encoding='utf-8')
        
        logger.info(f"✅ Extracted {len(df)} Instagram posts")
        logger.info(f"💾 Saved to: {output_file}")
        
        return df
        
    except Exception as e:
        logger.error(f"❌ Error extracting Instagram data: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def generate_sample_instagram_data():
    """
    Generate sample Instagram data for testing
    (Digunakan jika Access Token belum dikonfigurasi)
    """
    logger.info("📝 Generating sample Instagram data...")
    
    sample_data = []
    
    # 20 sample posts dengan data realistis
    for i in range(1, 21):
        post = {
            'post_id': f'SAMPLE_POST_{i:03d}',
            'caption': f'Sample Instagram post #{i} - Nourish Beauty product showcase 💄✨ #NourishBeauty #Makeup #Beauty',
            'media_type': 'IMAGE' if i % 3 != 0 else 'VIDEO',
            'media_url': f'https://sample-cdn.instagram.com/post_{i}.jpg',
            'permalink': f'https://www.instagram.com/p/sample_{i}/',
            'post_timestamp': (datetime.now() - pd.Timedelta(days=i)).isoformat(),
            'like_count': 150 + (i * 10),
            'comments_count': 20 + (i * 2),
            'reach': 1000 + (i * 50),
            'impressions': 1500 + (i * 80),
            'engagement': 170 + (i * 12),
            'saved': 30 + (i * 3),
            'load_timestamp': datetime.now()
        }
        
        # Calculate engagement rate
        post['engagement_rate'] = round((post['engagement'] / post['reach']) * 100, 2)
        
        sample_data.append(post)
    
    df = pd.DataFrame(sample_data)
    
    # Save sample data
    output_file = os.path.join(
        PATHS['external'], 
        f"instagram_SAMPLE_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    )
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    logger.info(f"✅ Generated {len(df)} sample Instagram posts")
    logger.info(f"💾 Saved to: {output_file}")
    
    return df

def load_to_staging_db(df):
    """Load Instagram data to staging_instagram table"""
    if df is None or len(df) == 0:
        logger.warning("⚠️  No Instagram data to load")
        return
    
    try:
        logger.info("🔄 Loading Instagram data to staging_instagram...")
        
        engine = get_engine()
        
        # Truncate first
        with engine.connect() as conn:
            conn.execute("TRUNCATE TABLE staging_instagram")
            conn.commit()
        
        # Select relevant columns matching staging table
        columns_to_load = ['post_id', 'caption', 'media_type', 'media_url', 
                          'post_timestamp', 'like_count', 'comments_count', 
                          'reach', 'impressions', 'engagement_rate']
        
        df_load = df[[col for col in columns_to_load if col in df.columns]].copy()
        
        # Convert timestamp to datetime
        df_load['post_timestamp'] = pd.to_datetime(df_load['post_timestamp'])
        
        # Load data
        df_load.to_sql('staging_instagram', engine, if_exists='append', index=False, method='multi')
        
        logger.info(f"✅ Loaded {len(df_load)} rows to staging_instagram")
        
    except Exception as e:
        logger.error(f"❌ Error loading to staging: {e}")
        raise

if __name__ == "__main__":
    # Test extraction
    df = extract_instagram_posts()
    
    if df is not None:
        print(f"\n📊 Instagram Data Preview:")
        print(df.head())
        print(f"\n📈 Shape: {df.shape}")
        print(f"\n📊 Engagement Stats:")
        print(df[['like_count', 'comments_count', 'reach', 'engagement_rate']].describe())
        
        # Load to database
        load_to_staging_db(df)
    else:
        print("\n⚠️  No Instagram data extracted")
