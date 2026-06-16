import { useSearchParams } from 'react-router-dom';
import { ProvinceGrid } from '../components/explore/ProvinceGrid';
import { DealerBrowser } from '../components/explore/DealerBrowser';
import '../components/explore/explore.css';

export function Explore() {
  const [params, setParams] = useSearchParams();
  const prov = params.get('prov');

  return (
    <div className="container explore">
      {prov ? (
        <DealerBrowser key={prov} prov={prov} />
      ) : (
        <ProvinceGrid onPick={(code) => setParams({ prov: code })} />
      )}
    </div>
  );
}
