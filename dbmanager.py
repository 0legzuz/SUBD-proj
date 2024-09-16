from PyQt5.QtCore import *
import pymysql
from pymysql.cursors import *
import os


# Update ntp_proj set PFIN4 = PFIN - 3*Round(PFIN/4);

class dbc():
    dbcon = None

def checkconfig(name):
    if not os.path.exists(name):
        f = open(name, 'w')
        f.write("""[DB]
Host=localhost
User=root
Pass=root
DBName=nir""")
        f.close()



def openDatabase(dbini):
    ini = QSettings(dbini, QSettings.IniFormat)
    ini.setIniCodec("utf-8")
    ini.beginGroup("DB")
    dbname = ini.value("DBName")
    dbuser = ini.value("User")
    dbpass = ini.value("Pass")
    dbhost = ini.value("Host")
    ini.endGroup()

    try:
        con = pymysql.connect(dbhost, dbuser , dbpass, dbname, cursorclass=DictCursor)
        print("database '" +dbname+"' is open OK")
        dbc.dbcon = con
        return con
    except BaseException:
        print("cannot connect to database")
        return None

def countNPROJ():
    with dbc.dbcon.cursor() as cur:
        cur.execute("SELECT CODPROG, count(*) cnt FROM ntp_proj GROUP by CODPROG order by Codprog")
        ntp_prog_cnt = cur.fetchall()

        cur.execute("SET SQL_SAFE_UPDATES = 0")
        for row in ntp_prog_cnt:
            q = "UPDATE ntp_prog SET nproj = {} WHERE TRIM(codprog) = {}".format(row['cnt'], row['CODPROG'])
            cur.execute(q)
        dbc.dbcon.commit()

def SumPFinInProg():
    with dbc.dbcon.cursor() as cur:
        cur.execute("select codprog ,sum(PFIN) pfin,sum(PFIN1) pfin1,sum(PFIN2) pfin2,sum(PFIN3) pfin3,sum(PFIN4) pfin4 from nir.ntp_proj Group by ntp_proj.codprog")
        ntp_prog_pfin_sum = cur.fetchall()

        cur.execute("SET SQL_SAFE_UPDATES = 0")
        for row in ntp_prog_pfin_sum:
            q = "UPDATE ntp_prog SET pfin = {},pfin1 = {},pfin2 = {},pfin3 = {},pfin4 = {} WHERE TRIM(codprog) = {}".format(row['pfin'],row['pfin1'],row['pfin2'],row['pfin3'],row['pfin4'], row['codprog'])
            cur.execute(q)
        dbc.dbcon.commit()

def SumFFinInProg():
    with dbc.dbcon.cursor() as cur:
        cur.execute("select codprog ,sum(FFIN) FFIN,sum(FFIN1) FFIN1,sum(FFIN2) FFIN2,sum(FFIN3) FFIN3,sum(FFIN4) FFIN4 from nir.ntp_proj Group by ntp_proj.codprog")
        ntp_prog_FFIN_sum = cur.fetchall()

        cur.execute("SET SQL_SAFE_UPDATES = 0")
        for row in ntp_prog_FFIN_sum:
            q = "UPDATE ntp_prog SET FFIN = {},FFIN1 = {},FFIN2 = {},FFIN3 = {},FFIN4 = {} WHERE TRIM(codprog) = {}".format(row['FFIN'],row['FFIN1'],row['FFIN2'],row['FFIN3'],row['FFIN4'], row['codprog'])
            cur.execute(q)
        dbc.dbcon.commit()


def GetTableNir(sort = 0, desc = False, filter = None):
    sorttuple = ('order by pj.Codprog, pj.F',
                 'order by pj.isp',
                 'order by pj.Pfin')
    descsorttuple = ('order by pj.Codprog desc, pj.F desc',
                 'order by pj.isp desc',
                 'order by pj.Pfin desc')
    if desc :
        sortexpr = descsorttuple[sort]
    else:
        sortexpr = sorttuple[sort]

    filterexpr = getFilter(filter,"pg","v")

    with dbc.dbcon.cursor() as cur:
        query = f"""SELECT pg.PROG, pj.F,  pj.isp, pj.PFIN, pj.FFIN,pj.SROK_N, pj.SROK_K,pj.RUK, pj.GRNTI, pj.CODTYPE,pj.PFIN1,pj.PFIN2,pj.PFIN3,pj.PFIN4,pj.FFIN1,pj.FFIN2,pj.FFIN3,pj.FFIN4, pj.NIR FROM nir.ntp_proj pj, nir.ntp_prog pg, vuz v 
where pj.CODPROG = pg.CODPROG and trim(v.codvuz) = trim(pj.CODISP) {filterexpr}  {sortexpr}"""
        # print(query)
        cur.execute(query)
        table = cur.fetchall()
        return table

def GetProgTable():
    with dbc.dbcon.cursor() as cur:
        cur.execute("SELECT CODPROG, PROG, NPROJ, PFIN,PFIN1,PFIN2,PFIN3,PFIN4, FFIN,FFIN1,FFIN2,FFIN3,FFIN4 FROM nir.ntp_prog ")
        table = cur.fetchall()

        cur.execute(f"select codprog from nir.ntp_prog where prog = 'Экраноплан'")
        # print(cur.fetchone()["codprog"])
        # cprog =
        return table

def GetVuzTable():
    with dbc.dbcon.cursor() as cur:
        cur.execute("SELECT * FROM nir.vuz ")
        table = cur.fetchall()
        return table

def GetProgTuple():
    with dbc.dbcon.cursor() as cur:
        cur.execute("SELECT PROG FROM nir.ntp_prog ")
        progtup = ((row["PROG"]) for row in cur.fetchall())
        return tuple(progtup)

def GetMaxProjInProg(prog):
    with dbc.dbcon.cursor() as cur:
        cur.execute(f"SELECT max(pj.F) F FROM nir.ntp_prog pg, nir.ntp_proj pj where pg.prog = '{prog}' and pg.codprog = pj.codprog")
        i = cur.fetchone()["F"]
        if not i:
            i = 0
        return i

def GetVuzTuple():
    with dbc.dbcon.cursor() as cur:
        cur.execute("SELECT z2 FROM nir.vuz ")
        vuztup = ((row["z2"]) for row in cur.fetchall())
        return tuple(vuztup)

def CheckProjNum(prog,num):
    with dbc.dbcon.cursor() as cur:
        cur.execute(f"SELECT pj.F FROM nir.ntp_prog pg, nir.ntp_proj pj where pg.prog = '{prog}' and pg.codprog = pj.codprog")
        nums = tuple(int(row["F"]) for row in cur.fetchall())
        return not (num in nums)

def AddRecord(prog,f,nir,isp,srn,srk,ruk,ruk2,grnti,ctype,pfin):
    with dbc.dbcon.cursor() as cur:
        cur.execute(f"select codprog from nir.ntp_prog where prog = '{prog}'")
        row  = cur.fetchone()
        cprog = row["codprog"]
        cur.execute(f"select codvuz from nir.vuz where z2 = '{isp}'")
        cisp = cur.fetchone()["codvuz"].strip()
        # print(cisp)
        pfin = int(pfin)
        pfin123 = round(pfin/4)
        pfin4 = pfin - 3 * round(pfin / 4)

        cur.execute(f"""INSERT INTO nir.ntp_proj (CODPROG,F,NIR,ISP,CODISP,SROK_N,SROK_K,RUK,RUK2,GRNTI,CODTYPE,PFIN,PFIN1,PFIN2,PFIN3,PFIN4,FFIN,FFIN1,FFIN2,FFIN3,FFIN4)
VALUES('{cprog}','{str(f).rjust(4,"0")}','{nir}','{isp}','{cisp}','{srn}','{srk}','{ruk}','{ruk2}','{grnti}','{ctype}',{pfin},{pfin123},{pfin123},{pfin123},{pfin4},0,0,0,0,0)""")

        dbc.dbcon.commit()

def EditRecord(prog,f,nir,isp,srn,srk,ruk,ruk2,grnti,ctype,pfin):
    with dbc.dbcon.cursor() as cur:
        cur.execute(f"select codprog from nir.ntp_prog where prog = '{prog}'")
        row  = cur.fetchone()
        cprog = row["codprog"]
        cur.execute(f"select codvuz from nir.vuz where z2 = '{isp}'")
        cisp = cur.fetchone()["codvuz"].strip()
        print(cisp)
        pfin = int(pfin)
        print(str(pfin))
        pfin123 = round(pfin/4)
        pfin4 = pfin - 3 * round(pfin / 4)

        cur.execute(f"""Replace INTO nir.ntp_proj (CODPROG,F,NIR,ISP,CODISP,SROK_N,SROK_K,RUK,RUK2,GRNTI,CODTYPE,PFIN,PFIN1,PFIN2,PFIN3,PFIN4,FFIN,FFIN1,FFIN2,FFIN3,FFIN4)
        VALUES('{cprog}','{str(f).rjust(4, "0")}','{nir}','{isp}','{cisp}','{srn}','{srk}','{ruk}','{ruk2}','{grnti}','{ctype}',{pfin},{pfin123},{pfin123},{pfin123},{pfin4},0,0,0,0,0)""")

#         cur.execute(f"""Update nir.ntp_proj set CODPROG = '{cprog}',F = '{str(f).rjust(4,"0")}',NIR = '{nir}',ISP= '{isp}',CODISP= '{cisp}',SROK_N = '{srn}',SROK_K = '{srk}',
# RUK='{ruk}',RUK2='{ruk2}',GRNTI='{grnti}',CODTYPE='{ctype}',PFIN={pfin},PFIN1={pfin123},PFIN2={pfin123},PFIN3={pfin123},PFIN4= {pfin4}""")

        dbc.dbcon.commit()

def RemoveRecord(prog,f):
    with dbc.dbcon.cursor() as cur:
        # cur.execute(f"select codprog from nir.ntp_prog where prog = '{prog}'")
        # row  = cur.fetchone()
        # cprog = row["codprog"]
        cur.execute(f"delete from ntp_proj using ntp_proj, ntp_prog  where ntp_prog.prog = '{prog}' and ntp_prog.codprog = ntp_proj.codprog and ntp_proj.f = '{f}'")
        dbc.dbcon.commit()


def GetRecord(prog,f):
    with dbc.dbcon.cursor() as cur:
        cur.execute(f"select nj.CODPROG,nj.F,nj.NIR,nj.ISP,nj.CODISP,nj.SROK_N,nj.SROK_K,nj.RUK,nj.RUK2,nj.GRNTI,nj.CODTYPE,nj.PFIN from  nir.ntp_proj nj,nir.ntp_prog ng where ng.prog = '{prog}' and ng.codprog = nj.codprog and nj.f = '{f}'")
        return cur.fetchone()


def GetFullGeoinfo():
    geoinfo = {'region':None,'oblname':None,'city':None,'z2':None}

    for geo in geoinfo:
        if not geoinfo[geo]:
            geoinfo[geo] = GetGeoList(geo)

    return geoinfo


def GetGeoList(geo, name= None):
    if name:
        geoname = f"where {geo.upper()} = {name}"
    else:
        geoname = ""

    with dbc.dbcon.cursor() as cur:
        cur.execute(f"SELECT distinct {geo.upper()} FROM vuz {geoname}")
        geolist = [(row[geo.upper()]) for row in cur.fetchall()]
    return list(geolist)


def GetGeoinfo(field, name):

    with dbc.dbcon.cursor() as cur:
        cur.execute(f"SELECT  region, oblname, city, z2 FROM vuz where {field} = '{name}'")
        table = cur.fetchall()
        reg  = {(row["region"]) for row in table}
        obl = {(row["oblname"]) for row in table}
        city = {(row["city"]) for row in table}
        vuz = {(row["z2"]) for row in table}

    return {'region':reg,'oblname':obl,'city':city,'z2':vuz}

def GetAnalisTable(i,filter = {}):

    filterexpr = getFilter(filter,"pg","v")

    querys = [
            f"""SELECT v.codvuz, v.z2, "NPROG", COUNT(pj.F) NPROJ, SUM(pj.PFIN) PFIN FROM ntp_proj pj, ntp_prog pg, vuz v 
WHERE pj.CODPROG = pg.CODPROG and trim(v.codvuz) = trim(pj.CODISP) {filterexpr}  GROUP BY v.codvuz ORDER BY v.codvuz""",
            f"""SELECT pg.CODPROG, pg.PROG, count(*) NPROJ, sum(pj.PFIN) PFIN, "NVUZ" FROM ntp_proj pj, ntp_prog pg, vuz v 
WHERE pj.CODPROG = pg.CODPROG and trim(v.codvuz) = trim(pj.CODISP) {filterexpr} GROUP BY pg.CODPROG order by pg.CODPROG""",
            f"""SELECT pj.CODTYPE, COUNT(pj.F) NPROJ, SUM(pj.PFIN) PFIN FROM ntp_proj pj, ntp_prog pg, vuz v 
    where pj.CODPROG = pg.CODPROG and trim(v.codvuz) = trim(pj.CODISP) {filterexpr} GROUP BY pj.CODTYPE"""
    ]


    if i >= len(querys):
        print("wrong query number")
        return -1

    with dbc.dbcon.cursor() as cur:
        cur.execute(querys[i])
        table = cur.fetchall()
        cnt = {}
        if i == 0:
            col, cnt = groopVuzProg("ISP",filterexpr)
            table = replaceColumn(table,col,'z2','NPROG')

        if i == 1:
            col, cnt = groopVuzProg("CODPROG",filterexpr)
            table = replaceColumn(table,col,'CODPROG','NVUZ')

        if i == 2:
            fulltype = {"Ф": "Фундаментальное исследование",
                        "П": "Прикладное исседование",
                        "Р": "Экспериментальная разработка"}
            for row in table:
                row["CODTYPE"] = fulltype[row["CODTYPE"]]

        empty = ["CODPROG","codvuz"]
        vsego = ['z2','PROG','CODTYPE']
        itog = dict(zip(table[0],[0,]*len(table[0])))

        for row in table:
            for key,val in row.items():
                if key not in empty+vsego:
                    itog[key] += val

        for key in itog:
            if key in empty:
                itog[key] = ""
                continue
            if key in vsego:
                itog[key] = "Всего"
                continue
            if key in cnt.keys():
                itog[key] = cnt[key]
                continue

        table.append(itog)


        return table


def replaceColumn(table,columngroop,keyname,valname,):
    for row in table:
        for key, val in columngroop.items():
            if row[keyname] == key:
                row[valname] = val
                columngroop.pop(key)
                break
    return table


def groopVuzProg(keycolumn, filter=""):
    """
        Группирует либо программы по вузом, либо вузы по программам. Считает сколько всего уникальных вузов/программ.
            keycolumn -- "ISP"/"CODPROG" -- по чему группировать
            filter -- выдражение для фильтрации
    """
    columns = ["ISP", "CODPROG"]
    cnttitle = ["NVUZ", "NPROG"]
    if keycolumn not in columns:
        return -1

    j = 1 - columns.index(keycolumn)

    subquery = (
        f"""SELECT distinct pj.ISP, pj.CODPROG FROM ntp_proj pj, ntp_prog pg, vuz v 
    WHERE trim(v.codvuz)=trim(pj.CODISP) and pg.CODPROG=pj.CODPROG {filter}""",
        f"""SELECT distinct pj.{columns[j]} FROM ntp_proj pj, ntp_prog pg, vuz v 
    WHERE trim(v.codvuz)=trim(pj.CODISP) and pg.CODPROG=pj.CODPROG {filter}"""
    )

    with dbc.dbcon.cursor() as cur:
        cur.execute(subquery[0])
        table = cur.fetchall()

        groop = {}
        for row in table:
            key = row[keycolumn]

            if key not in groop.keys():
                groop[key] = 0

            groop[key] += 1

        cur.execute(subquery[1])
        cnt = {cnttitle[j]:len(cur.fetchall())}

        return groop, cnt


def getFilter(filter,ntp_prog = "ntp_prog",vuz = "vuz"):
    filterexpr = ""

    if filter:
        if "prog" in filter.keys():
            filterexpr += f"and {ntp_prog}.PROG = '{filter['prog']}' "

        if "geo" in filter.keys():
            geofilter = filter['geo']
            for f,n in geofilter.items():
                filterexpr += f"and trim({vuz}.{f}) = trim('{n}') "

    return filterexpr

def getSumFin():

    with dbc.dbcon.cursor() as cur:
        cur.execute(f"SELECT  sum(pfin) pfin,sum(ffin) ffin FROM ntp_proj")
        fin = cur.fetchone()
    return fin

def NirVuzFinDistribute(sumpfin,orderfin):
    ffpintable = {}
    with dbc.dbcon.cursor() as cur:
        cur.execute(f"SELECT codprog, f, isp, floor(pfin/{sumpfin}*{orderfin}) ffin FROM ntp_proj")
        ffpintable['nir'] = cur.fetchall()
        cur.execute(f"SELECT isp, sum(floor(pfin/{sumpfin}*{orderfin})) ffin FROM ntp_proj group by isp")
        ffpintable['vuz'] = cur.fetchall()
    return ffpintable

def AddFFinToNir(fintable,nquart):
    with dbc.dbcon.cursor() as cur:
        for row in fintable:
            q = f"UPDATE ntp_proj SET FFIN = FFIN + {row['ffin']}, FFIN{nquart} = FFIN{nquart} + {row['ffin']} WHERE TRIM(codprog) = {row['codprog']} and TRIM(F) = {row['f']}"

            cur.execute(q)

        dbc.dbcon.commit()




if __name__ == '__main__':

    db = openDatabase("config.ini")



