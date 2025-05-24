import os
from core.genflow import Node

class FetchJiraStories(Node):
    def prep(self, shared):
        print("\nDEBUG: Starting FetchJiraStories prep")
        
        # Get Jira credentials and configuration from environment variables
        # or let users pass them as command line arguments
        jira_url = os.environ.get("JIRA_URL", shared.get("jira_url"))
        jira_username = os.environ.get("JIRA_USERNAME", shared.get("jira_username"))
        jira_api_token = os.environ.get("JIRA_API_TOKEN", shared.get("jira_api_token"))
        jira_project_key = os.environ.get("JIRA_PROJECT_KEY", shared.get("jira_project_key", "XYZ"))
        output_dir = shared.get("output_dir", "analysis_output")
        
        # DEBUG FLAG - Set to True to use sample data instead of real Jira
        # In production, set this to False
        use_sample_data = False
        
        # If any of the required credentials are missing, use sample data
        if not jira_url or not jira_username or not jira_api_token:
            print("Warning: Jira credentials not found. Using sample data instead.")
            use_sample_data = True
        
        if use_sample_data:
            print("Using sample Jira data for testing")
            return {"use_sample": True, "output_dir": output_dir, "project_key": jira_project_key}
            
        return {"use_sample": False, "jira_url": jira_url, "jira_username": jira_username, 
                "jira_api_token": jira_api_token, "project_key": jira_project_key, "output_dir": output_dir}
        
    def exec(self, prep_res):
        if not prep_res:
            # Skip Jira integration if credentials aren't available
            print("Skipping Jira integration due to missing credentials")
            return None
            
        # Check if we should use sample data
        if prep_res.get("use_sample", False):
            return self._generate_sample_stories(prep_res["project_key"], prep_res["output_dir"])
            
        jira_url = prep_res["jira_url"]
        jira_username = prep_res["jira_username"]
        jira_api_token = prep_res["jira_api_token"]
        jira_project_key = prep_res["project_key"]
        output_dir = prep_res["output_dir"]
        
        try:
            from jira import JIRA
            
            print(f"Connecting to Jira at {jira_url} with username {jira_username}")
            print(f"Using project key: {jira_project_key}")
            
            # Connect to Jira
            try:
                jira = JIRA(
                    server=jira_url,
                    basic_auth=(jira_username, jira_api_token)
                )
                
                # Verify connection by trying to access the server info
                server_info = jira.server_info()
                print(f"Successfully connected to Jira server version: {server_info.get('version', 'unknown')}")
            except Exception as conn_error:
                print(f"Error connecting to Jira: {str(conn_error)}")
                return None
            
            # Search for issues that start with the specified project key
            try:
                jql_query = f'project = "{jira_project_key}" ORDER BY updated DESC'
                print(f"Executing JQL query: {jql_query}")
                issues = jira.search_issues(jql_query, maxResults=10)
                print(f"Found {len(issues)} Jira issues")
            except Exception as query_error:
                print(f"Error searching for Jira issues: {str(query_error)}")
                return None
            
            if not issues:
                print(f"No issues found for project key: {jira_project_key}")
                return []
                
            # Extract relevant information from each issue
            stories = []
            for issue in issues:
                print(f"Processing issue: {issue.key}")
                # Get issue details
                story = {
                    'key': issue.key,
                    'summary': issue.fields.summary,
                    'status': issue.fields.status.name,
                    'description': issue.fields.description or '',
                    'created': issue.fields.created,
                    'updated': issue.fields.updated,
                    'comments': [],
                    'attachments': []
                }
                
                # Get comments
                if hasattr(issue.fields, 'comment'):
                    for comment in issue.fields.comment.comments:
                        story['comments'].append({
                            'author': comment.author.displayName,
                            'body': comment.body,
                            'created': comment.created
                        })
                
                # Get attachments - especially images
                if hasattr(issue.fields, 'attachment'):
                    for attachment in issue.fields.attachment:
                        is_image = attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))
                        
                        # For images, save them locally
                        attachment_data = {
                            'filename': attachment.filename,
                            'created': attachment.created,
                            'is_image': is_image,
                            'content_type': attachment.mimeType,
                            'size': attachment.size
                        }
                        
                        if is_image:
                            try:
                                # Download image and save it
                                image_data = jira.download_attachment(attachment.id)
                                attachments_dir = os.path.join(output_dir, 'jira_attachments')
                                os.makedirs(attachments_dir, exist_ok=True)
                                
                                image_path = os.path.join(attachments_dir, attachment.filename)
                                with open(image_path, 'wb') as f:
                                    f.write(image_data)
                                    
                                # Store relative path for embedding in HTML
                                # Use a relative path that works in HTML context
                                attachment_data['local_path'] = f"jira_attachments/{attachment.filename}"
                                print(f"Saved attachment: {image_path}")
                            except Exception as e:
                                print(f"Error downloading attachment {attachment.filename}: {str(e)}")
                        
                        story['attachments'].append(attachment_data)
                
                stories.append(story)
            
            return stories
            
        except ImportError:
            print("Error: Jira package not installed. Please install it using 'pip install jira'.")
            return None
        except Exception as e:
            print(f"Error fetching Jira stories: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _generate_sample_stories(self, project_key, output_dir):
        """Generate sample Jira stories for testing"""
        print("Generating sample Jira stories for testing")
        
        # Create sample stories
        stories = []
        
        # Story 1 - Feature request with comments and attachments
        story1 = {
            'key': f'{project_key}-101',
            'summary': 'Implement Jira integration for code analyzer',
            'status': 'In Progress',
            'description': 'As a user, I want to see my relevant Jira stories in the code analysis report so that I can track issues related to my codebase.\n\n**Acceptance Criteria:**\n- Fetch stories from Jira API\n- Display summary, status, and description\n- Show comments and attachments\n- Integrate with existing report',
            'created': '2023-05-15T10:30:00.000+0000',
            'updated': '2023-05-16T14:45:00.000+0000',
            'comments': [
                {
                    'author': 'John Developer',
                    'body': 'I\'ve started working on this. Initial API connection is working.',
                    'created': '2023-05-15T15:22:00.000+0000'
                },
                {
                    'author': 'Maria Manager',
                    'body': 'Great! Make sure to handle authentication errors gracefully.',
                    'created': '2023-05-15T16:05:00.000+0000'
                }
            ],
            'attachments': []
        }
        
        # Story 2 - Bug report
        story2 = {
            'key': f'{project_key}-102',
            'summary': 'Fix broken CSS in report generation',
            'status': 'To Do',
            'description': 'The CSS styles in the generated report are not being applied correctly. The Jira stories section is not displaying images properly.\n\n**Steps to reproduce:**\n1. Generate a report with Jira stories\n2. Open the HTML report\n3. Notice the images are not displayed',
            'created': '2023-05-17T09:15:00.000+0000',
            'updated': '2023-05-17T09:15:00.000+0000',
            'comments': [],
            'attachments': []
        }
        
        # Story 3 - Completed task
        story3 = {
            'key': f'{project_key}-100',
            'summary': 'Set up project structure and dependencies',
            'status': 'Done',
            'description': 'Create the initial project structure with requirements.txt, main.py, and necessary modules.',
            'created': '2023-05-10T08:00:00.000+0000',
            'updated': '2023-05-12T16:30:00.000+0000',
            'comments': [
                {
                    'author': 'John Developer',
                    'body': 'Completed and ready for review.',
                    'created': '2023-05-12T15:45:00.000+0000'
                },
                {
                    'author': 'Sarah Reviewer',
                    'body': 'Looks good! Approved.',
                    'created': '2023-05-12T16:30:00.000+0000'
                }
            ],
            'attachments': []
        }
        
        # Add the stories to the list
        stories.extend([story1, story2, story3])
        
        # Create sample image attachments
        try:
            import random
            from PIL import Image, ImageDraw, ImageFont
            
            # Create directory for attachments
            attachments_dir = os.path.join(output_dir, 'jira_attachments')
            os.makedirs(attachments_dir, exist_ok=True)
            
            # Create sample images
            for i, color in enumerate([
                (255, 200, 200),  # Light red
                (200, 255, 200),  # Light green
                (200, 200, 255)   # Light blue
            ]):
                # Create a colored image with text
                img = Image.new('RGB', (400, 300), color=color)
                draw = ImageDraw.Draw(img)
                
                # Add some text
                text = f"Sample Jira Attachment {i+1}"
                draw.text((20, 20), text, fill=(0, 0, 0))
                
                # Draw some shapes
                draw.rectangle([(50, 50), (350, 250)], outline=(0, 0, 0))
                
                # Save the image
                filename = f"sample_attachment_{i+1}.png"
                img_path = os.path.join(attachments_dir, filename)
                img.save(img_path)
                
                # Add to the first story
                if i == 0:
                    story1['attachments'].append({
                        'filename': filename,
                        'created': '2023-05-16T10:30:00.000+0000',
                        'is_image': True,
                        'content_type': 'image/png',
                        'size': os.path.getsize(img_path),
                        'local_path': f"jira_attachments/{filename}"
                    })
                
            print(f"Created sample image attachments in {attachments_dir}")
            
        except ImportError:
            print("Warning: PIL/Pillow not installed. Skipping sample image generation.")
        except Exception as e:
            print(f"Error creating sample images: {str(e)}")
        
        print(f"Generated {len(stories)} sample Jira stories")
        return stories
    
    def post(self, shared, prep_res, exec_res):
        if exec_res:
            print(f"\nFetched {len(exec_res)} Jira stories")
            shared["jira_stories"] = exec_res
        else:
            print("No Jira stories fetched or error occurred")
            shared["jira_stories"] = []
            
        return "default" 