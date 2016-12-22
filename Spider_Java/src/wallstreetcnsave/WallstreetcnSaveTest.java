package wallstreetcnsave;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.text.DateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import com.mongodb.BasicDBObject;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.Mongo;

public class WallstreetcnSaveTest implements Runnable {
	
	private static String DataBaseName = "textclassify";
	private static String CollectionName = "WallstreetSaveJava";

	private static String url = "http://api.wallstreetcn.com/v2/livenews?&page=";
	
	private static String Regex = ".*?\"type\":\"(.*?)\".*?\"contentHtml\":\"<p>(.*?)<\\\\/p>\".*?\"categorySet\":\"(.*?)\".*?";
	private static final String REGEXSTRING1 = "type";
	private static final String REGEXSTRING2 = "content";
	private static final String REGEXSTRING3 = "categoryset";
	
	//map表的存放
	public static Map<String, String> GetMap() {
		Map<String, String> map = new HashMap<String, String>();
		map.put("1", "外汇");
		map.put("2", "股市");
		map.put("3", "商品");
		map.put("4", "债市");
		map.put("9", "中国");
		map.put("10", "美国");
		map.put("11", "欧元区");
		map.put("12", "日本");
		map.put("13", "英国");
		map.put("14", "澳洲");
		map.put("15", "加拿大");
		map.put("16", "瑞士");
		map.put("17", "其他地区");
		map.put("5", "央行");
		return map;
	}
	private static String[] ruleList_district = { "9", "10", "11", "12", "13", "14", "15", "16", "17" };
	private static String[] ruleList_property = { "1", "2", "3", "4" };
	private static String[] ruleList_centralbank = { "5" };
	
	private static final int start = 1;
	private static final int end = 3000;
	
	//对x,x,x格式的内容进行分隔筛选
	public static String setCategory(String categorySet, String[] ruleList, Map<String, String> map) {
		StringBuffer disStr = new StringBuffer(); 
		String[] strArray = null;
		strArray = categorySet.split(","); // 拆分字符为",",然后把结果交给数组strArray
		// 获取需要的信息
		int length_strArray = strArray.length;
		int length_ruleList = ruleList.length;
		
		if (length_strArray > 0) {
			for (int iArr = 0; iArr < length_strArray; iArr++) {
				String s = strArray[iArr];
					for (int iRul=0; iRul < length_ruleList; iRul++) {
						if (s.equals(ruleList[iRul])) {
							disStr.append(map.get(s));
							disStr.append(",");
								break;
							}
						}
				}
			}
			if(disStr.length()>1) {
				disStr = disStr.deleteCharAt(disStr.length()-1);
			}
			return disStr.toString();
		}
	
	//读取整个页面，返回html字符串
	private static String httpRequest(String requestUrl) {
		StringBuffer buffer = null;
		BufferedReader bufferedReader = null;
		InputStreamReader inputStreamReader = null;
		InputStream inputStream = null;
		HttpURLConnection httpUrlConn = null;
		try {
			// 建立get请求
			URL url = new URL(requestUrl);
			httpUrlConn = (HttpURLConnection) url.openConnection();
			httpUrlConn.setDoInput(true);
			httpUrlConn.setRequestMethod("GET");
			// 获取输入流
			inputStream = httpUrlConn.getInputStream();
			inputStreamReader = new InputStreamReader(inputStream, "UTF-8");
			bufferedReader = new BufferedReader(inputStreamReader);
			// 从输入流获取结果
			buffer = new StringBuffer();
			String str = null;
			while ((str = bufferedReader.readLine()) != null) {
				str = new String(str.getBytes(), "UTF-8");
				buffer.append(str);
			}
		} catch (Exception e) {
			e.printStackTrace();
		} finally {
			if (bufferedReader != null) {
				try {
					bufferedReader.close();
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
			if (inputStreamReader != null) {
				try {
					inputStreamReader.close();
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
			if (inputStream != null) {
				try {
					inputStream.close();
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
			if (httpUrlConn != null) {
				httpUrlConn.disconnect();
			}
		}
		return buffer.toString();
	}

	// 过滤掉无用的信息
	public static List<Map<String, String>> htmlFiter(String html, String Regex) {
		List<Map<String, String>> list = new ArrayList<Map<String, String>>();
		// 查找目标
		Pattern p = Pattern.compile(Regex);
		Matcher m = p.matcher(html);
		while (m.find()) {
			Map<String, String> map_save = new HashMap<String, String>();
			// 可修改部分
			map_save.put(REGEXSTRING1, m.group(1));
			map_save.put(REGEXSTRING2, m.group(2));
			map_save.put(REGEXSTRING3, m.group(3));
			
			list.add(map_save);
		}
		return list;
	}
	
	//unicode格式转中文
	public static String UnicodeToString(String str) {
			Pattern pattern = Pattern.compile("(\\\\u(\\p{XDigit}{4}))"); // XDigit表示16进制数字，正则里的\p表示Unicode块
			Matcher matcher = pattern.matcher(str);
			char ch;
			while (matcher.find()) {
				ch = (char) Integer.parseInt(matcher.group(2), 16); // 16进制转10进制作为ascii码，再char转为字符
				str = str.replace(matcher.group(1), ch + "");
			}
			return str;
		}
	
	public void run() {
		// 链接数据库
		try {
			Mongo mongo = new Mongo("localhost", 27017);
			DB db = mongo.getDB(DataBaseName);
			DBCollection collection = db.getCollection(CollectionName);
			
			// 调用抓取的方法获取内容
			for (int i = start; i <= end; i++) {
				String requestUrl = url + i;
				System.out.println(requestUrl);
				
				String html = httpRequest(requestUrl);
				List<Map<String, String>> resultList = htmlFiter(html, Regex);
				
				if (resultList.isEmpty()) {
					System.out.printf("The end url: %s", requestUrl);
					break;
				} else {
					for (Map<String, String> result : resultList) {
						BasicDBObject dbObject = new BasicDBObject();
						
						String type = result.get(REGEXSTRING1);
						String content = UnicodeToString(result.get(REGEXSTRING2));
//						String content = result.get(REGEXSTRING2);
						
						Map<String, String> map = GetMap();
						String district = setCategory(result.get(REGEXSTRING3), ruleList_district, map); 
						String property = setCategory(result.get(REGEXSTRING3), ruleList_property, map);
						String centralbank = setCategory(result.get(REGEXSTRING3), ruleList_centralbank, map);
						
						Date date = new Date();
						DateFormat time = DateFormat.getDateTimeInstance();
						String time_str = time.format(date);
						
						String source = "wangstreetcn";

						dbObject.put("content", content);       // 具体内容
						dbObject.put("createdtime", time_str);   // 创建时间
						dbObject.put("source", source);          // 信息来源
						dbObject.put("district", district);      // 所属地区
						dbObject.put("property", property);      // 资产类别
						dbObject.put("centralbank", centralbank); // 资产类别
						dbObject.put("type", type); //信息类型
						
						collection.insert(dbObject);
					}
				}
			}
		} catch (Exception e) {
			e.printStackTrace();
		} 
	}
	
	
	public static void main(String[] args) throws InterruptedException {
		WallstreetcnSaveTest wallstreetcnsave = new WallstreetcnSaveTest();
		wallstreetcnsave.run();
	}

}
