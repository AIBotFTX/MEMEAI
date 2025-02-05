# **MEME_AI**

## **How to Launch**

Follow these steps to set up and run MEME_AI using Docker:

1. **Create a Docker directory** (outside the `memeai` folder):  
   ```bash
   cd .. && mkdir docker
   ```

2. **Move the `composer.yml` file** to the new `docker` directory:  
   ```bash
   mv composer.yml docker/composer.yml
   ```

3. **Navigate to the `docker` directory**:  
   ```bash
   cd docker
   ```

4. **Build and start the containers using Docker Compose**:  
   ```bash
   docker compose -f composer.yml up --build
   ```

---

### **Notes:**
- Ensure you have **Docker** and **Docker Compose** installed.
- Run the above commands from the root project directory.
- Use `docker compose down` to stop and remove the containers when done.