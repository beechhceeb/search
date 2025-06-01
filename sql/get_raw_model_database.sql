with
  model_brand as (
    select
      model_id
      , brand
      , primary_category
      , secondary_category
      , product_type
      , product_system
    from `{read_project}.{daw_dataset}.SMV`
  )

  , current_model_performance as (
    select
      model_id
      , model_name
      , performance_group
    , count_of_buy_products
      , case
        when market = 'eu' then 'EU'
        when market = 'uk' then 'UK'
        when market = 'us' then 'US'
      end
        as market
    from
      `{read_project}.{daw_dataset}.model_performance_group_history`
    where
      report_date = (
        select max(report_date)
        from `{read_project}.{daw_dataset}.model_performance_group_history`
      )
      -- Currently filtering out models that are not in the top 100 or best seller groups
      and performance_group in ('Top 100', 'Best Seller')
  )

select
  p.model_id
  , p.model_name
  , p.market
  , p.performance_group
  , p.count_of_buy_products
  , b.primary_category
  , b.secondary_category
  , b.product_type
  , b.product_system
  , b.brand
from current_model_performance as p
  inner join model_brand as b
    on p.model_id = b.model_id
where
  1 = 1
  -- Two unexplained duplite models
  and not (p.model_id = 63266 and b.brand = 'Nikon')
  and not (p.model_id = 63465 and b.brand = 'Tamron')
order by
  p.count_of_buy_products desc
