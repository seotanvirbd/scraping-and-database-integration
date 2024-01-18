from playwright.sync_api import sync_playwright
import psycopg2
from psycopg2.extras import execute_values
from doctest import master
from psycopg2 import extras

def main():
    with sync_playwright() as p:
        
        #scrape data
        browser = p.chromium.launch(headless= False,slow_mo=1000)
        page = browser.new_page()
        page.goto('https://coinmarketcap.com/',timeout=60000) 
        page.wait_for_load_state('domcontentloaded')
        
        #scrolling down
        for i in range(5):
            page.mouse.wheel(0,2000)
            page.wait_for_timeout(1000)
        
        trs_xpath = '//*[@id="__next"]/div[2]/div/div[2]/div/div[1]/div[4]/table/tbody/tr'
        trs_list = page.query_selector_all(trs_xpath)
        # print(len(trs_list))
        
        master_list =[]
            
        for tr in trs_list:
            coin_dict= {}
            
            tds = tr.query_selector_all('//td')
            
            coin_dict['id'] = tds[1].inner_text()
            coin_dict['Name'] = tds[2].query_selector('//p[@color="text"]').inner_text()
            coin_dict['Symbol'] = tds[2].query_selector('//p[@color="text3"]').inner_text()
            coin_dict['Price_usd'] = float(tds[3].inner_text().replace('$','').replace(',','').replace('.',''))

            coin_dict['Market_cap_usd'] = int(tds[7].inner_text().replace('$','').replace('.','').replace(',',''))
            coin_dict['Volue_24h_usd'] = int(tds[8].query_selector('//p[@color="text"]').inner_text().replace('$','').replace('.','').replace(',',''))
            master_list.append(coin_dict)
        # print(master_list)    
        ###save data
        list_of_tuples = [tuple(dic.values()) for dic in master_list]
        #connet to daae
        pgconn = psycopg2.connect(
            host = 'localhost',
            database = 'postgres',
           
            user = 'postgres',
            password = '1234'
        )
        
        #create cursor
        pgcursor = pgconn.cursor()
        
        execute_values(pgcursor,
                       "INSERT INTO crypto_currency(id,name, symbol,Price_usd,market_cap_usd, volume_24h_usd) VALUES %s",
                       list_of_tuples)
        
        # commit
        pgconn.commit()
        
        #close connection
        pgconn.close()
        
        
        browser.close()
if __name__ == '__main__':
    main()
