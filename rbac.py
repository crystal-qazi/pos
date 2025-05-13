import mysql.connector
from mysql.connector import Error


class RBACManager:
    def __init__(self, host, database, user, password):
        self.connection = None
        try:
            self.connection = mysql.connector.connect(
                host=host,
                database='pharma',
                user='root',
                password='root'
            )
            self._initialize_database()
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
    
    def _initialize_database(self):
        """Create necessary tables if they don't exist"""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS roles (
                role_id INT AUTO_INCREMENT PRIMARY KEY,
                role_name VARCHAR(50) NOT NULL UNIQUE,
                description TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS user_roles (
                user_id INT NOT NULL,
                role_id INT NOT NULL,
                PRIMARY KEY (user_id, role_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS permissions (
                permission_id INT AUTO_INCREMENT PRIMARY KEY,
                permission_name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS role_permissions (
                role_id INT NOT NULL,
                permission_id INT NOT NULL,
                PRIMARY KEY (role_id, permission_id),
                FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE,
                FOREIGN KEY (permission_id) REFERENCES permissions(permission_id) ON DELETE CASCADE
            )
            """
        ]
        
        cursor = self.connection.cursor()
        for query in queries:
            cursor.execute(query)
        self.connection.commit()
        cursor.close()
    
    def create_role(self, role_name, description=None):
        """Create a new role"""
        query = "INSERT INTO roles (role_name, description) VALUES (%s, %s)"
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (role_name, description))
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error creating role: {e}")
            return None
        finally:
            cursor.close()
    
    def create_user(self, username, password, email=None):
        """Create a new user"""
        query = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (username, password, email))
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error creating user: {e}")
            return None
        finally:
            cursor.close()
    
    def assign_role_to_user(self, user_id, role_id):
        """Assign a role to a user"""
        query = "INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)"
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (user_id, role_id))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error assigning role to user: {e}")
            return False
        finally:
            cursor.close()
    
    def create_permission(self, permission_name, description=None):
        """Create a new permission"""
        query = "INSERT INTO permissions (permission_name, description) VALUES (%s, %s)"
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (permission_name, description))
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error creating permission: {e}")
            return None
        finally:
            cursor.close()
    
    def assign_permission_to_role(self, role_id, permission_id):
        """Assign a permission to a role"""
        query = "INSERT INTO role_permissions (role_id, permission_id) VALUES (%s, %s)"
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (role_id, permission_id))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error assigning permission to role: {e}")
            return False
        finally:
            cursor.close()
    
    def check_user_permission(self, user_id, permission_name):
        """Check if a user has a specific permission"""
        query = """
        SELECT COUNT(*) FROM users u
        JOIN user_roles ur ON u.user_id = ur.user_id
        JOIN role_permissions rp ON ur.role_id = rp.role_id
        JOIN permissions p ON rp.permission_id = p.permission_id
        WHERE u.user_id = %s AND p.permission_name = %s
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (user_id, permission_name))
            result = cursor.fetchone()
            return result[0] > 0
        except Error as e:
            print(f"Error checking user permission: {e}")
            return False
        finally:
            cursor.close()
    
    def get_user_roles(self, user_id):
        """Get all roles assigned to a user"""
        query = """
        SELECT r.role_id, r.role_name, r.description 
        FROM roles r
        JOIN user_roles ur ON r.role_id = ur.role_id
        WHERE ur.user_id = %s
        """
        cursor = self.connection.cursor(dictionary=True)
        try:
            cursor.execute(query, (user_id,))
            return cursor.fetchall()
        except Error as e:
            print(f"Error getting user roles: {e}")
            return []
        finally:
            cursor.close()
    
    def close(self):
        """Close the database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()

# Example usage
if __name__ == "__main__":
    # Initialize RBAC manager with your MySQL credentials
    rbac = RBACManager(
        host="localhost",
        database="rbac_demo",
        user="your_username",
        password="your_password"
    )
    
    try:
        # Create roles
        admin_role_id = rbac.create_role("admin", "Administrator with full access")
        editor_role_id = rbac.create_role("editor", "Can edit content")
        viewer_role_id = rbac.create_role("viewer", "Can view content only")
        
        # Create permissions
        create_perm_id = rbac.create_permission("create", "Create content")
        read_perm_id = rbac.create_permission("read", "Read content")
        update_perm_id = rbac.create_permission("update", "Update content")
        delete_perm_id = rbac.create_permission("delete", "Delete content")
        
        # Assign permissions to roles
        rbac.assign_permission_to_role(admin_role_id, create_perm_id)
        rbac.assign_permission_to_role(admin_role_id, read_perm_id)
        rbac.assign_permission_to_role(admin_role_id, update_perm_id)
        rbac.assign_permission_to_role(admin_role_id, delete_perm_id)
        
        rbac.assign_permission_to_role(editor_role_id, create_perm_id)
        rbac.assign_permission_to_role(editor_role_id, read_perm_id)
        rbac.assign_permission_to_role(editor_role_id, update_perm_id)
        
        rbac.assign_permission_to_role(viewer_role_id, read_perm_id)
        
        # Create a user
        user_id = rbac.create_user("johndoe", "securepassword", "john@example.com")
        
        # Assign roles to user
        rbac.assign_role_to_user(user_id, admin_role_id)
        
        # Check permissions
        print(f"Can user create? {rbac.check_user_permission(user_id, 'create')}")
        print(f"Can user delete? {rbac.check_user_permission(user_id, 'delete')}")
        
        # Get user roles
        roles = rbac.get_user_roles(user_id)
        print("User roles:")
        for role in roles:
            print(f"- {role['role_name']}")
            
    finally:
        rbac.close()