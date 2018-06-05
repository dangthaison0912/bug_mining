USING setup_backend.sh
1) Install postgresql for your enviroment
2) run setup_backend.sh
3) when you get to the point for setting user confirm your password and as "postgres" do
 3.1) run the command "psql"
 3.2) to create user input this : CREATE foofighter WITH PASSWORD 'dleifynot';
 3.3) to create db, input this: CREATE DATABASE doctimetable_default_db;
 3.4) to assign user the access level : GRANT ALL PRIVILEGES ON DATABASE doctimetable_default_db TO foofighter;
 3.5) to exit : \q
4) it should continue by setting up npm installations
