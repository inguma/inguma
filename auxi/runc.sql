CREATE OR REPLACE AND COMPILE JAVA SOURCE NAMED "RunC" AS
import java.io.*; 
public class RunC{ 
    public static String Run(String cmd){
        try{
            Process p = Runtime.getRuntime().exec(cmd);
            BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream()));
            String line = null;
            String result = "";

            while((line = br.readLine()) != null) {
                result += line + "\n");
            }

            return(result);
        }
            catch (Exception e){
                return(e.getMessage()); 
        }
    }
}
/
