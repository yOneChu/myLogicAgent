-- ==============================================================================
-- [SQL 쿼리명] V호기 전용 제품-자재 BOM(PARTOFEBOM) extraction 쿼리
-- [작성일자] 2026-09-12
-- [설명] PLM 시스템에 등록된 V로 시작하는 호기(제품)들의 유효(WIP) BOM 명세 및 사양 정보를 추출합니다.
-- [참조명세] reference/db_metadata/[명세서]_제품자재_BOM_조회분석.md
-- ==============================================================================

-- 1. 유효버전(WIP) V호기 OID 추출 서브쿼리 정의
WITH ouid AS (
    SELECT A.vf$ouid AS VFOID
      FROM HDEL_DEFAULT.product$vf A, 
           HDEL_DEFAULT.product$id B
     WHERE A.vf$identity = B.id$ouid            -- 유효버전(WIP) 연결 조건 1
       AND A.vf$ouid     = B.id$wip             -- 유효버전(WIP) 연결 조건 2
       AND A.MD$NUMBER LIKE 'V%'                -- V로 시작하는 호기번호 조건
       AND A.MD$NUMBER NOT LIKE 'TEST%'         -- 테스트 호기 제외 (고정 필터)
       AND A.MD$NUMBER NOT LIKE 'Q%'            -- 견적 호기 제외 (고정 필터)
       -- AND A.MD$STATUS = 'RLS'               -- [선택] 릴리즈(승인) 제품만 조회 시 주석 해제
       -- AND SUBSTR(A.MD$MDATE, 1, 4) = '2026'  -- [선택] 특정 수정연도 필터링 시 주석 해제
)
-- 2. 제품-자재 BOM 정보 및 주요 영업사양, 자재마스터 정보 조인 및 추출
SELECT 
    -- 제품(호기) 마스터 정보
    (SELECT MD$NUMBER FROM HDEL_DEFAULT.PRODUCT$VF WHERE VF$OUID = PE.PRODUCTOUID) AS PARENTNO,
    (SELECT F.VF$VERSION FROM HDEL_DEFAULT.PRODUCT$VF F WHERE F.VF$OUID = PE.PRODUCTOUID) AS PARENT_VER,
    (SELECT PRODUCT.MD$STATUS FROM HDEL_DEFAULT.PRODUCT$VF PRODUCT WHERE PRODUCT.VF$OUID = PE.PRODUCTOUID) AS PROD_STATUS,
    (SELECT CASE WHEN LENGTH(PRODUCT.MD$CDATE) >= 8 
                 THEN SUBSTR(PRODUCT.MD$CDATE, 1, 4) || '-' || SUBSTR(PRODUCT.MD$CDATE, 5, 2) || '-' || SUBSTR(PRODUCT.MD$CDATE, 7, 2)
                 ELSE PRODUCT.MD$CDATE END
       FROM HDEL_DEFAULT.PRODUCT$VF PRODUCT WHERE PRODUCT.VF$OUID = PE.PRODUCTOUID) AS PROD_CDATE,
    (SELECT CASE WHEN LENGTH(PRODUCT.MD$MDATE) >= 8 
                 THEN SUBSTR(PRODUCT.MD$MDATE, 1, 4) || '-' || SUBSTR(PRODUCT.MD$MDATE, 5, 2) || '-' || SUBSTR(PRODUCT.MD$MDATE, 7, 2)
                 ELSE PRODUCT.MD$MDATE END
       FROM HDEL_DEFAULT.PRODUCT$VF PRODUCT WHERE PRODUCT.VF$OUID = PE.PRODUCTOUID) AS PROD_MODDATE,

    -- 영업사양 (상관 서브쿼리 패턴 + COD 변환)
    (SELECT HDEL_DEFAULT.COD(E.EL_ATYP) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
      WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip
        AND E.MD$NUMBER = (SELECT F.MD$NUMBER FROM HDEL_DEFAULT.PRODUCT$VF F WHERE F.VF$OUID = PE.PRODUCTOUID)
        AND ROWNUM = 1) AS GISONG,
    (SELECT HDEL_DEFAULT.COD(E.EL_ABRAND) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
      WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip
        AND E.MD$NUMBER = (SELECT F.MD$NUMBER FROM HDEL_DEFAULT.PRODUCT$VF F WHERE F.VF$OUID = PE.PRODUCTOUID)
        AND ROWNUM = 1) AS BRAND,
    (SELECT HDEL_DEFAULT.COD(E.EL_ASPD) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
      WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip
        AND E.MD$NUMBER = (SELECT F.MD$NUMBER FROM HDEL_DEFAULT.PRODUCT$VF F WHERE F.VF$OUID = PE.PRODUCTOUID)
        AND ROWNUM = 1) AS EL_ASPD,
    (SELECT HDEL_DEFAULT.COD(E.EL_ACAPA) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
      WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip
        AND E.MD$NUMBER = (SELECT F.MD$NUMBER FROM HDEL_DEFAULT.PRODUCT$VF F WHERE F.VF$OUID = PE.PRODUCTOUID)
        AND ROWNUM = 1) AS EL_ACAPA,
    (SELECT HDEL_DEFAULT.COD(E.EL_ASPSCD) FROM HDEL_DEFAULT.ELV_INFO$ID A, HDEL_DEFAULT.ELV_INFO$VF E
      WHERE A.ID$OUID = E.VF$IDENTITY AND E.vf$ouid = A.id$wip
        AND E.MD$NUMBER = (SELECT F.MD$NUMBER FROM HDEL_DEFAULT.PRODUCT$VF F WHERE F.VF$OUID = PE.PRODUCTOUID)
        AND ROWNUM = 1) AS ASPSCD,

    -- 자재(Part) 마스터 정보
    NP.MD$NUMBER            AS PARTNO,       -- 자재번호(품번)
    NP.MD$DESC              AS PARTNAME,     -- 자재명(품명)
    NP.VF$VERSION           AS PART_VERSION,  -- 자재 버전
    NVL(NP.SPEC, '')        AS SPEC,         -- 자재 SPEC
    NVL(NP.G_L_CODE, '')    AS GLCODE,       -- G/L 계정코드
    
    -- BOM 적용 정보
    PE.QTY                  AS PART_QTY,     -- 소요 수량
    PE.CMT                  AS CMT,          -- BOM 적용조건/비고

    -- 자재 변동정보
    VP.UCHECK               AS UCHECK        -- 수정 확인 여부

  FROM HDEL_DEFAULT.PARTOFEBOM PE
 INNER JOIN HDEL_DEFAULT.NORMALPART$VF NP 
    ON PE.PARTOUID = NP.VF$OUID              -- BOM 행 -> 자재 조인
  LEFT OUTER JOIN HDEL_DEFAULT.VARIABLEPART_NEW VP
    ON VP.PRODUCTOUID = PE.PRODUCTOUID 
   AND VP.ASSOOUID    = PE.ASSOOUID          -- BOM 행 -> 변동정보 (OUTER JOIN)
 WHERE PE.PRODUCTOUID IN (SELECT VFOID FROM ouid)
 ORDER BY PARENTNO, PARTNO;
