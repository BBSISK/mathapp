"""
TOPIC MANAGEMENT MODULE
========================
This module adds topic, strand, and tutorial management to the AgentMath.app app.
Import this at the end of app.py to enable the admin topic management features.

Usage in app.py:
    # At the very end of app.py, add:
    from topic_management import register_topic_routes
    register_topic_routes(app, db)
"""

from flask import jsonify, request
from sqlalchemy import text
from functools import wraps
from datetime import datetime
import json

# ==================== DATABASE MODELS ====================
# These need to be created via migration script first

def get_strand_model(db):
    """Strand model - curriculum strands like Number, Algebra, etc."""
    class Strand(db.Model):
        __tablename__ = 'strands'
        __table_args__ = {'extend_existing': True}
        
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), unique=True, nullable=False)
        color = db.Column(db.String(20), default='#667eea')
        icon = db.Column(db.String(10), default='📚')
        description = db.Column(db.Text)
        sort_order = db.Column(db.Integer, default=0)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        def to_dict(self):
            return {
                'id': self.id,
                'name': self.name,
                'color': self.color,
                'icon': self.icon,
                'description': self.description,
                'sort_order': self.sort_order
            }
    
    return Strand

def get_topic_model(db):
    """Topic model - individual topics within strands"""
    class Topic(db.Model):
        __tablename__ = 'topics'
        __table_args__ = {'extend_existing': True}
        
        id = db.Column(db.Integer, primary_key=True)
        topic_id = db.Column(db.String(50), unique=True, nullable=False)  # e.g., 'arithmetic'
        display_name = db.Column(db.String(100), nullable=False)  # e.g., 'Arithmetic'
        icon = db.Column(db.String(50), default='book')  # Font Awesome icon name
        strand_id = db.Column(db.Integer, db.ForeignKey('strands.id'))
        sort_order = db.Column(db.Integer, default=0)
        is_visible = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def to_dict(self):
            return {
                'id': self.id,
                'topic_id': self.topic_id,
                'display_name': self.display_name,
                'icon': self.icon,
                'strand_id': self.strand_id,
                'sort_order': self.sort_order,
                'is_visible': self.is_visible
            }
    
    return Topic

def get_tutorial_model(db):
    """Tutorial model - splash screen content for each topic/difficulty"""
    class Tutorial(db.Model):
        __tablename__ = 'tutorials'
        __table_args__ = {'extend_existing': True}
        
        id = db.Column(db.Integer, primary_key=True)
        topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
        difficulty = db.Column(db.String(20), nullable=False)  # beginner, intermediate, advanced
        title = db.Column(db.String(200), nullable=False)
        introduction = db.Column(db.Text)
        principles = db.Column(db.Text)  # JSON string
        examples = db.Column(db.Text)  # JSON string
        tips = db.Column(db.Text)  # JSON string
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
        
        def to_dict(self):
            return {
                'id': self.id,
                'topic_id': self.topic_id,
                'difficulty': self.difficulty,
                'title': self.title,
                'introduction': self.introduction,
                'principles': json.loads(self.principles) if self.principles else [],
                'examples': json.loads(self.examples) if self.examples else [],
                'tips': json.loads(self.tips) if self.tips else []
            }
    
    return Tutorial


def register_topic_routes(app, db):
    """Register all topic management routes with the Flask app"""
    
    # Get or create models
    Strand = get_strand_model(db)
    Topic = get_topic_model(db)
    Tutorial = get_tutorial_model(db)
    
    # Helper to invalidate topic cache when topics are modified
    def invalidate_topics_cache():
        """Clear the topics cache so changes take effect immediately"""
        try:
            from app import invalidate_topics_cache as app_invalidate
            app_invalidate()
            print("✓ Topics cache invalidated")
        except ImportError:
            # Function not available in app.py yet - that's OK
            pass
        except Exception as e:
            print(f"Warning: Could not invalidate cache: {e}")
    
    # Helper to check if user is admin
    def admin_required_api(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import session
            if 'user_id' not in session:
                return jsonify({'error': 'Not logged in'}), 401
            from app import User
            user = User.query.get(session['user_id'])
            if not user or user.role != 'admin':
                return jsonify({'error': 'Admin access required'}), 403
            return f(*args, **kwargs)
        return decorated_function
    
    # ==================== STRAND ROUTES ====================
    
    @app.route('/api/admin/strands', methods=['GET'])
    @admin_required_api
    def get_all_strands():
        """Get all strands"""
        try:
            strands = db.session.execute(text(
                "SELECT * FROM strands ORDER BY sort_order"
            )).fetchall()
            
            return jsonify([{
                'id': s[0],
                'name': s[1],
                'color': s[2],
                'icon': s[3],
                'description': s[4],
                'sort_order': s[5]
            } for s in strands])
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/strands', methods=['POST'])
    @admin_required_api
    def create_strand():
        """Create a new strand"""
        data = request.json
        try:
            db.session.execute(text("""
                INSERT INTO strands (name, color, icon, description, sort_order)
                VALUES (:name, :color, :icon, :description, :sort_order)
            """), {
                'name': data['name'],
                'color': data.get('color', '#667eea'),
                'icon': data.get('icon', '📚'),
                'description': data.get('description', ''),
                'sort_order': data.get('sort_order', 0)
            })
            db.session.commit()
            return jsonify({'success': True, 'message': 'Strand created'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/strands/<int:strand_id>', methods=['PUT'])
    @admin_required_api
    def update_strand(strand_id):
        """Update a strand"""
        data = request.json
        try:
            db.session.execute(text("""
                UPDATE strands 
                SET name = :name, color = :color, icon = :icon, 
                    description = :description, sort_order = :sort_order
                WHERE id = :id
            """), {
                'id': strand_id,
                'name': data['name'],
                'color': data.get('color', '#667eea'),
                'icon': data.get('icon', '📚'),
                'description': data.get('description', ''),
                'sort_order': data.get('sort_order', 0)
            })
            db.session.commit()
            return jsonify({'success': True, 'message': 'Strand updated'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/strands/<int:strand_id>', methods=['DELETE'])
    @admin_required_api
    def delete_strand(strand_id):
        """Delete a strand (only if no topics assigned)"""
        try:
            # Check if any topics are assigned
            topics = db.session.execute(text(
                "SELECT COUNT(*) FROM topics WHERE strand_id = :id"
            ), {'id': strand_id}).fetchone()[0]
            
            if topics > 0:
                return jsonify({'error': f'Cannot delete: {topics} topics are assigned to this strand'}), 400
            
            db.session.execute(text("DELETE FROM strands WHERE id = :id"), {'id': strand_id})
            db.session.commit()
            return jsonify({'success': True, 'message': 'Strand deleted'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/strands/<int:strand_id>/reorder', methods=['POST'])
    @admin_required_api
    def reorder_strand(strand_id):
        """Move strand up or down in order"""
        try:
            direction = request.json.get('direction', 'up')
            
            # Get current strand
            current = db.session.execute(text(
                "SELECT id, sort_order FROM strands WHERE id = :id"
            ), {'id': strand_id}).fetchone()
            
            if not current:
                return jsonify({'error': 'Strand not found'}), 404
            
            current_order = current[1]
            
            if direction == 'up':
                # Find the strand above (lower sort_order)
                neighbor = db.session.execute(text("""
                    SELECT id, sort_order FROM strands 
                    WHERE sort_order < :current_order 
                    ORDER BY sort_order DESC LIMIT 1
                """), {'current_order': current_order}).fetchone()
            else:
                # Find the strand below (higher sort_order)
                neighbor = db.session.execute(text("""
                    SELECT id, sort_order FROM strands 
                    WHERE sort_order > :current_order 
                    ORDER BY sort_order ASC LIMIT 1
                """), {'current_order': current_order}).fetchone()
            
            if neighbor:
                # Swap sort_orders
                db.session.execute(text(
                    "UPDATE strands SET sort_order = :new_order WHERE id = :id"
                ), {'new_order': neighbor[1], 'id': strand_id})
                db.session.execute(text(
                    "UPDATE strands SET sort_order = :new_order WHERE id = :id"
                ), {'new_order': current_order, 'id': neighbor[0]})
                db.session.commit()
            
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    # ==================== TOPIC ROUTES ====================
    
    @app.route('/api/admin/topics-management', methods=['GET'])
    @admin_required_api
    def get_all_topics_admin():
        """Get all topics with strand info for admin management"""
        try:
            topics = db.session.execute(text("""
                SELECT t.id, t.topic_id, t.display_name, t.icon, t.strand_id, 
                       t.sort_order, t.is_visible, s.name as strand_name,
                       (SELECT COUNT(*) FROM questions q WHERE q.topic = t.topic_id) as question_count,
                       (SELECT COUNT(*) FROM tutorials tu WHERE tu.topic_id = t.id) as tutorial_count
                FROM topics t
                LEFT JOIN strands s ON t.strand_id = s.id
                ORDER BY s.sort_order, t.sort_order
            """)).fetchall()
            
            return jsonify([{
                'id': t[0],
                'topic_id': t[1],
                'display_name': t[2],
                'icon': t[3],
                'strand_id': t[4],
                'sort_order': t[5],
                'is_visible': bool(t[6]),
                'strand_name': t[7],
                'question_count': t[8],
                'tutorial_count': t[9]
            } for t in topics])
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/topics-management', methods=['POST'])
    @admin_required_api
    def create_topic():
        """Create a new topic"""
        data = request.json
        try:
            # Validate topic_id (slug format)
            topic_id = data['topic_id'].lower().strip().replace(' ', '_')
            
            # Check for duplicates
            existing = db.session.execute(text(
                "SELECT id FROM topics WHERE topic_id = :topic_id"
            ), {'topic_id': topic_id}).fetchone()
            
            if existing:
                return jsonify({'error': f'Topic ID "{topic_id}" already exists'}), 400
            
            db.session.execute(text("""
                INSERT INTO topics (topic_id, display_name, icon, strand_id, sort_order, is_visible)
                VALUES (:topic_id, :display_name, :icon, :strand_id, :sort_order, :is_visible)
            """), {
                'topic_id': topic_id,
                'display_name': data['display_name'],
                'icon': data.get('icon', 'book'),
                'strand_id': data.get('strand_id'),
                'sort_order': data.get('sort_order', 0),
                'is_visible': data.get('is_visible', True)
            })
            db.session.commit()
            invalidate_topics_cache()
            return jsonify({'success': True, 'message': 'Topic created', 'topic_id': topic_id})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/topics-management/<int:topic_db_id>', methods=['PUT'])
    @admin_required_api
    def update_topic(topic_db_id):
        """Update a topic"""
        data = request.json
        try:
            db.session.execute(text("""
                UPDATE topics 
                SET display_name = :display_name, icon = :icon, strand_id = :strand_id,
                    sort_order = :sort_order, is_visible = :is_visible,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :id
            """), {
                'id': topic_db_id,
                'display_name': data['display_name'],
                'icon': data.get('icon', 'book'),
                'strand_id': data.get('strand_id'),
                'sort_order': data.get('sort_order', 0),
                'is_visible': data.get('is_visible', True)
            })
            db.session.commit()
            invalidate_topics_cache()
            return jsonify({'success': True, 'message': 'Topic updated'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/topics-management/<int:topic_db_id>', methods=['DELETE'])
    @admin_required_api
    def delete_topic(topic_db_id):
        """Delete a topic (only if no questions exist)"""
        try:
            # Get topic_id first
            topic = db.session.execute(text(
                "SELECT topic_id FROM topics WHERE id = :id"
            ), {'id': topic_db_id}).fetchone()
            
            if not topic:
                return jsonify({'error': 'Topic not found'}), 404
            
            topic_id = topic[0]
            
            # Check if any questions exist
            questions = db.session.execute(text(
                "SELECT COUNT(*) FROM questions WHERE topic = :topic_id"
            ), {'topic_id': topic_id}).fetchone()[0]
            
            if questions > 0:
                return jsonify({'error': f'Cannot delete: {questions} questions exist for this topic'}), 400
            
            # Delete tutorials first
            db.session.execute(text("DELETE FROM tutorials WHERE topic_id = :id"), {'id': topic_db_id})
            
            # Delete topic
            db.session.execute(text("DELETE FROM topics WHERE id = :id"), {'id': topic_db_id})
            db.session.commit()
            invalidate_topics_cache()
            return jsonify({'success': True, 'message': 'Topic deleted'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/topics-management/<int:topic_db_id>/visibility', methods=['PUT'])
    @admin_required_api
    def toggle_topic_visibility(topic_db_id):
        """Toggle topic visibility"""
        data = request.json
        try:
            db.session.execute(text("""
                UPDATE topics SET is_visible = :is_visible, updated_at = CURRENT_TIMESTAMP
                WHERE id = :id
            """), {
                'id': topic_db_id,
                'is_visible': data.get('is_visible', True)
            })
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/topics-management/<int:topic_db_id>/reorder', methods=['POST'])
    @admin_required_api
    def reorder_topic(topic_db_id):
        """Move topic up or down in order within its strand"""
        try:
            direction = request.json.get('direction', 'up')
            
            # Get current topic
            current = db.session.execute(text(
                "SELECT id, sort_order, strand_id FROM topics WHERE id = :id"
            ), {'id': topic_db_id}).fetchone()
            
            if not current:
                return jsonify({'error': 'Topic not found'}), 404
            
            current_order = current[1]
            strand_id = current[2]
            
            if direction == 'up':
                # Find the topic above (lower sort_order) within same strand
                neighbor = db.session.execute(text("""
                    SELECT id, sort_order FROM topics 
                    WHERE sort_order < :current_order 
                    AND (strand_id = :strand_id OR (:strand_id IS NULL AND strand_id IS NULL))
                    ORDER BY sort_order DESC LIMIT 1
                """), {'current_order': current_order, 'strand_id': strand_id}).fetchone()
            else:
                # Find the topic below (higher sort_order) within same strand
                neighbor = db.session.execute(text("""
                    SELECT id, sort_order FROM topics 
                    WHERE sort_order > :current_order 
                    AND (strand_id = :strand_id OR (:strand_id IS NULL AND strand_id IS NULL))
                    ORDER BY sort_order ASC LIMIT 1
                """), {'current_order': current_order, 'strand_id': strand_id}).fetchone()
            
            if neighbor:
                # Swap sort_orders
                db.session.execute(text(
                    "UPDATE topics SET sort_order = :new_order, updated_at = CURRENT_TIMESTAMP WHERE id = :id"
                ), {'new_order': neighbor[1], 'id': topic_db_id})
                db.session.execute(text(
                    "UPDATE topics SET sort_order = :new_order, updated_at = CURRENT_TIMESTAMP WHERE id = :id"
                ), {'new_order': current_order, 'id': neighbor[0]})
                db.session.commit()
            
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    # ==================== TUTORIAL ROUTES ====================
    
    @app.route('/api/admin/tutorials/<int:topic_db_id>', methods=['GET'])
    @admin_required_api
    def get_topic_tutorials(topic_db_id):
        """Get all tutorials for a topic"""
        try:
            tutorials = db.session.execute(text("""
                SELECT id, topic_id, difficulty, title, introduction, principles, examples, tips
                FROM tutorials
                WHERE topic_id = :topic_id
                ORDER BY 
                    CASE difficulty 
                        WHEN 'beginner' THEN 1 
                        WHEN 'intermediate' THEN 2 
                        WHEN 'advanced' THEN 3 
                    END
            """), {'topic_id': topic_db_id}).fetchall()
            
            return jsonify([{
                'id': t[0],
                'topic_id': t[1],
                'difficulty': t[2],
                'title': t[3],
                'introduction': t[4],
                'principles': json.loads(t[5]) if t[5] else [],
                'examples': json.loads(t[6]) if t[6] else [],
                'tips': json.loads(t[7]) if t[7] else []
            } for t in tutorials])
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/tutorials', methods=['POST'])
    @admin_required_api
    def create_tutorial():
        """Create a new tutorial"""
        data = request.json
        try:
            # Check if tutorial already exists for this topic/difficulty
            existing = db.session.execute(text("""
                SELECT id FROM tutorials 
                WHERE topic_id = :topic_id AND difficulty = :difficulty
            """), {
                'topic_id': data['topic_id'],
                'difficulty': data['difficulty']
            }).fetchone()
            
            if existing:
                return jsonify({'error': 'Tutorial already exists for this topic/difficulty'}), 400
            
            db.session.execute(text("""
                INSERT INTO tutorials (topic_id, difficulty, title, introduction, principles, examples, tips)
                VALUES (:topic_id, :difficulty, :title, :introduction, :principles, :examples, :tips)
            """), {
                'topic_id': data['topic_id'],
                'difficulty': data['difficulty'],
                'title': data['title'],
                'introduction': data.get('introduction', ''),
                'principles': json.dumps(data.get('principles', [])),
                'examples': json.dumps(data.get('examples', [])),
                'tips': json.dumps(data.get('tips', []))
            })
            db.session.commit()
            return jsonify({'success': True, 'message': 'Tutorial created'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/tutorials/<int:tutorial_id>', methods=['PUT'])
    @admin_required_api
    def update_tutorial(tutorial_id):
        """Update a tutorial"""
        data = request.json
        try:
            db.session.execute(text("""
                UPDATE tutorials 
                SET title = :title, introduction = :introduction,
                    principles = :principles, examples = :examples, tips = :tips,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :id
            """), {
                'id': tutorial_id,
                'title': data['title'],
                'introduction': data.get('introduction', ''),
                'principles': json.dumps(data.get('principles', [])),
                'examples': json.dumps(data.get('examples', [])),
                'tips': json.dumps(data.get('tips', []))
            })
            db.session.commit()
            return jsonify({'success': True, 'message': 'Tutorial updated'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/tutorials/<int:tutorial_id>', methods=['DELETE'])
    @admin_required_api
    def delete_tutorial(tutorial_id):
        """Delete a tutorial"""
        try:
            db.session.execute(text("DELETE FROM tutorials WHERE id = :id"), {'id': tutorial_id})
            db.session.commit()
            return jsonify({'success': True, 'message': 'Tutorial deleted'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    # ==================== PUBLIC API ROUTES ====================
    # These replace the hardcoded topic data with database-driven data
    
    @app.route('/api/topics-config', methods=['GET'])
    def get_topics_config():
        """
        Get complete topic configuration from database.
        This is used by all dashboards to display topics dynamically.
        """
        try:
            # Get strands
            strands = db.session.execute(text(
                "SELECT id, name, color, icon, description, sort_order FROM strands ORDER BY sort_order"
            )).fetchall()
            
            # Get visible topics
            topics = db.session.execute(text("""
                SELECT t.topic_id, t.display_name, t.icon, t.strand_id, t.sort_order,
                       s.name as strand_name
                FROM topics t
                LEFT JOIN strands s ON t.strand_id = s.id
                WHERE t.is_visible = 1
                ORDER BY s.sort_order, t.sort_order
            """)).fetchall()
            
            # Build response
            strands_dict = {}
            strand_info = {}
            topic_names = {}
            topic_icons = {}
            
            for s in strands:
                strand_name = s[1]
                strand_info[strand_name] = {
                    'color': s[2],
                    'icon': s[3],
                    'description': s[4]
                }
                strands_dict[strand_name] = []
            
            for t in topics:
                topic_id = t[0]
                display_name = t[1]
                icon = t[2]
                strand_name = t[5]
                
                topic_names[topic_id] = display_name
                topic_icons[topic_id] = f'fa-{icon}'
                
                if strand_name and strand_name in strands_dict:
                    strands_dict[strand_name].append(topic_id)
            
            return jsonify({
                'strands': strands_dict,
                'strand_info': strand_info,
                'topic_names': topic_names,
                'topic_icons': topic_icons
            })
        except Exception as e:
            # Fallback to empty config if tables don't exist yet
            return jsonify({
                'strands': {},
                'strand_info': {},
                'topic_names': {},
                'topic_icons': {},
                'error': str(e)
            })
    
    @app.route('/api/tutorials/<topic_id>/<difficulty>', methods=['GET'])
    def get_tutorial_public(topic_id, difficulty):
        """Get tutorial content for student view"""
        try:
            # First get the topic's database ID
            topic = db.session.execute(text(
                "SELECT id FROM topics WHERE topic_id = :topic_id"
            ), {'topic_id': topic_id}).fetchone()
            
            if not topic:
                return jsonify({'error': 'Topic not found'}), 404
            
            tutorial = db.session.execute(text("""
                SELECT title, introduction, principles, examples, tips
                FROM tutorials
                WHERE topic_id = :topic_id AND difficulty = :difficulty
            """), {'topic_id': topic[0], 'difficulty': difficulty}).fetchone()
            
            if not tutorial:
                return jsonify({'exists': False})
            
            return jsonify({
                'exists': True,
                'title': tutorial[0],
                'introduction': tutorial[1],
                'principles': json.loads(tutorial[2]) if tutorial[2] else [],
                'examples': json.loads(tutorial[3]) if tutorial[3] else [],
                'tips': json.loads(tutorial[4]) if tutorial[4] else []
            })
        except Exception as e:
            return jsonify({'error': str(e), 'exists': False})
    
    print("✓ Topic management routes registered")
    return True
