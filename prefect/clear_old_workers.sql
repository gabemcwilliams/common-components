select * from prefect.public.worker
where status = 'OFFLINE';

delete from prefect.public.worker
where status = 'OFFLINE';